import os
import json
import uuid 
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import StateGraph, END
from state import GSTGraphState
from agents.reconciler import watcher_agent, reconciliation_agent
from agents.vendor_chase import vendor_chase_agent
from agents.optimizer_agent import optimizer_agent
from agents.erp_agent import erp_agent
<<<<<<< HEAD
from agents.filling_agent import filing_agent  # <-- NEW IMPORT
=======
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the StateGraph
workflow = StateGraph(GSTGraphState)

# 2. Add our agent nodes
workflow.add_node("watcher", watcher_agent)
workflow.add_node("reconciler", reconciliation_agent)
workflow.add_node("vendor_chase", vendor_chase_agent)
<<<<<<< HEAD
workflow.add_node("erp", erp_agent)
workflow.add_node("optimizer", optimizer_agent)
workflow.add_node("filing", filing_agent)  # <-- NEW NODE ADDED
=======
workflow.add_node("erp", erp_agent)             # <-- NEW NODE
workflow.add_node("optimizer", optimizer_agent)
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60

# 3. Define the Flow (Edges)
workflow.set_entry_point("watcher")
workflow.add_edge("watcher", "reconciler")
workflow.add_edge("reconciler", "vendor_chase")
workflow.add_edge("vendor_chase", "erp")
<<<<<<< HEAD
workflow.add_edge("erp", "optimizer")
workflow.add_edge("optimizer", "filing")   # <-- OPTIMIZER FLOWS TO FILING
workflow.add_edge("filing", END)           # <-- FILING IS THE FINAL STEP
=======
workflow.add_edge("erp", "optimizer")           # <-- ERP Engine goes to Optimizer
workflow.add_edge("optimizer", END)
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60

# --- 4. THE MONGODB CHECKPOINTER ---
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(mongo_uri)
checkpointer = MongoDBSaver(mongo_client, db_name="zero_touch_gst")

# Compile the app
gst_app = workflow.compile(checkpointer=checkpointer)

# ---------------------------------------------------------
# LOCAL TEST RUNNER
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Initializing Checkpointed LangGraph Orchestrator...\n")

    initial_state = {
        "current_period": "2026-03",
        "days_to_cutoff": 250,
        "books_data": [],
        "mismatches": [],
        "vendor_chase_log": [],
        "gstr3b_draft": {},
        "final_gstr3b": {},
        "hitl_flag": False
    }

    unique_run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": unique_run_id}}
    
    print(f"📁 Starting fresh run with Thread ID: {unique_run_id}")

    # Execute the Graph!
    final_state = gst_app.invoke(initial_state, config=config)

    print("\n" + "="*50)
    print("🏁 GRAPH EXECUTION COMPLETE (STATE SAVED TO MONGODB)")
    print("="*50)

<<<<<<< HEAD
    # --- Print Optimizer Report ---
    if final_state.get("hitl_flag"):
        draft = final_state.get("gstr3b_draft", {})
        print("\n📄 --- QUANTITATIVE AI OPTIMIZER REPORT ---")
        print(f"📊 Executive Brief: {draft.get('executive_brief')}")

    # --- Print FINAL GSTR-3B Table (Agent 6 Output) ---
    final_3b = final_state.get("final_gstr3b", {})
    if final_3b:
        print("\n📝 --- FINAL GSTR-3B DRAFT (AGENT 6) ---")
        tables = final_3b.get("tables", {})
        print(f"🔹 Table 3.1 (Outward Tax): ₹{tables.get('3_1_Outward_Supplies', 0):,.2f}")
        
        itc_table = tables.get("4_ITC", {})
        print(f"🔹 Table 4 (Net ITC Available): ₹{itc_table.get('4_C_Net_ITC_Available', 0):,.2f}")
        
        pay_table = tables.get("6_1_Payment", {})
        print(f"🔹 Table 6.1 (Net Cash Payable): ₹{pay_table.get('tax_payable_cash', 0):,.2f}")
        
        meta = final_3b.get("filing_meta", {})
        print(f"\n📅 Due Date: {meta.get('due_date')} | Status: {meta.get('filing_status')}")
=======
    if final_state.get("hitl_flag"):
        print("\n⚠️ WORKFLOW PAUSED: AWAITING HUMAN IN THE LOOP APPROVAL")
        print("\n📄 --- QUANTITATIVE AI OPTIMIZER REPORT ---")
        
        draft = final_state.get("gstr3b_draft", {})
        
        print(f"\n📊 Executive Brief:\n{draft.get('executive_brief', 'No brief generated.')}")
        
        print("\n🔍 Mismatch Variance Analysis:")
        mismatch_analysis = draft.get("mismatch_analysis") or []
        for rec in mismatch_analysis:
            print(f" 🔹 {rec.get('invoice_number', 'Unknown')}")
            print(f"    Variance: {rec.get('variance_calculation', 'N/A')}")
            print(f"    Action:   {rec.get('action_required', 'N/A')}\n")

        print("\n✅ RECOMMENDED TO CLAIM:")
        claimable = draft.get("recommended_to_claim") or []
        if not claimable:
            print(" - None recommended.")
        for item in claimable:
            print(f" - [{item.get('invoice_number', 'Unknown')} | ₹{item.get('itc_value', '0')}] : {item.get('financial_justification', 'No justification.')}")

        print("\n❌ RECOMMENDED TO DEFER / REVERSE:")
        unclaimable = draft.get("recommended_to_defer") or []
        if not unclaimable:
            print(" - None recommended.")
        for item in unclaimable:
            print(f" - [{item.get('invoice_number', 'Unknown')} | ₹{item.get('itc_value', '0')}] : {item.get('risk_assessment', 'No risk assessment.')}")
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
