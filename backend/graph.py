# backend/graph.py
import os
import json
import uuid  # <-- Added to generate unique run IDs
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import StateGraph, END
from state import GSTGraphState
from agents.reconciler import watcher_agent, reconciliation_agent
from agents.vendor_chase import vendor_chase_agent
from agents.optimizer_agent import optimizer_agent
from agents.erp_agent import erp_agent
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the StateGraph
workflow = StateGraph(GSTGraphState)

# 2. Add our agent nodes
workflow.add_node("watcher", watcher_agent)
workflow.add_node("reconciler", reconciliation_agent)
workflow.add_node("vendor_chase", vendor_chase_agent)
workflow.add_node("erp", erp_agent)             # <-- NEW NODE
workflow.add_node("optimizer", optimizer_agent)

# 3. Define the Flow (Edges)
workflow.set_entry_point("watcher")
workflow.add_edge("watcher", "reconciler")
workflow.add_edge("reconciler", "vendor_chase")
workflow.add_edge("vendor_chase", "erp")
workflow.add_edge("erp", "optimizer")           # <-- ERP Engine goes to Optimizer
workflow.add_edge("optimizer", END)

# --- 4. THE MONGODB CHECKPOINTER ---
# Ensure MONGO_URI is in your .env file! (Defaults to localhost if missing)
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(mongo_uri)

# This automatically creates a 'zero_touch_gst' database and manages state
checkpointer = MongoDBSaver(mongo_client, db_name="zero_touch_gst")

# Compile the app with the checkpointer
gst_app = workflow.compile(checkpointer=checkpointer)

# ---------------------------------------------------------
# LOCAL TEST RUNNER
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Initializing Checkpointed LangGraph Orchestrator...\n")

    initial_state = {
        "current_period": "2026-03",
        "days_to_cutoff": 250,
        "books_data": [
            {"invoice_number": "INV-1001", "vendor_gstin": "27AADCB2230M1Z2", "tax_amount": 9000.0},
            {"invoice_number": "INV-1002", "vendor_gstin": "29BBBCB1120K1Z5", "tax_amount": 21600.0},
            {"invoice_number": "INV-1003", "vendor_gstin": "33AAACA1111A1Z1", "tax_amount": 5000.0}
        ],
        "gstr2a_live_data": [],
        "gstr2b_static_data": [],
        "mismatches": [],
        "vendor_chase_log": [],
        "itc_recommendations": [],
        "gstr3b_draft": {},
        "hitl_flag": False,
        "workflow_status": "started"
    }

    # --- 5. DYNAMIC THREAD ID ---
    # Generate a random UUID so every test run is treated as a brand new session
    unique_run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": unique_run_id}}
    
    print(f"📁 Starting fresh run with Thread ID: {unique_run_id}")

    # Execute the Graph!
    final_state = gst_app.invoke(initial_state, config=config)

    print("\n" + "="*50)
    print("🏁 GRAPH EXECUTION COMPLETE (STATE SAVED TO MONGODB)")
    print("="*50)

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