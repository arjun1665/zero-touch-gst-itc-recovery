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
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the StateGraph
workflow = StateGraph(GSTGraphState)

# 2. Add our agent nodes
workflow.add_node("watcher", watcher_agent)
workflow.add_node("reconciler", reconciliation_agent)
workflow.add_node("vendor_chase", vendor_chase_agent)

# 3. Define the Flow
workflow.set_entry_point("watcher")
workflow.add_edge("watcher", "reconciler")
workflow.add_edge("reconciler", "vendor_chase")
workflow.add_edge("vendor_chase", END)

# ---------------------------------------------------------
# LOCAL TEST RUNNER
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Initializing MongoDB Checkpointed LangGraph...\n")
    
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

    # --- 4. THE MONGODB CHECKPOINTER ---
    # Ensure MONGODB_URI is in your .env file from earlier!
    mongo_uri = os.getenv("MONGO_URI")
    mongo_client = MongoClient(mongo_uri)
    
    # This automatically creates a 'zero_touch_gst' database and manages state
    checkpointer = MongoDBSaver(mongo_client, db_name="zero_touch_gst")
    
    # Compile the app with the checkpointer
    gst_app = workflow.compile(checkpointer=checkpointer)

    # --- 5. DYNAMIC THREAD ID ---
    # Generate a random UUID so every test run is treated as a brand new session
    unique_run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": unique_run_id}}
    
    print(f"📁 Starting fresh run with Thread ID: {unique_run_id}")

    # Execute the Graph!
    final_state = gst_app.invoke(initial_state, config=config)

    print("\n" + "="*50)
    print("🏁 GRAPH EXECUTION COMPLETE (STATE SAVED TO MONGODB ATLAS)")
    print("="*50)
    print(f"Total Mismatches Found: {len(final_state['mismatches'])}")
    for m in final_state['mismatches']:
        print(f" - {m.invoice_number} | Issue: {m.issue_type}")