# backend/graph.py
from langgraph.graph import StateGraph, END
from state import GSTGraphState
from agents.reconciler import watcher_agent, reconciliation_agent
import json
from agents.vendor_chase import vendor_chase_agent
# 1. Initialize the StateGraph with our Pydantic state schema
workflow = StateGraph(GSTGraphState)

# 2. Add our agent nodes to the graph
workflow.add_node("watcher", watcher_agent)
workflow.add_node("reconciler", reconciliation_agent)
workflow.add_node("vendor_chase", vendor_chase_agent)
# 3. Define the Flow (Edges)
# This tells LangGraph exactly what order to run the agents in.
workflow.set_entry_point("watcher")
workflow.add_edge("watcher", "reconciler")
# For now, it ends after reconciliation. We will add the Vendor Chase agent here later.
workflow.add_edge("reconciler", "vendor_chase")
workflow.add_edge("vendor_chase", END)
# 4. Compile the application
gst_app = workflow.compile()

# ---------------------------------------------------------
# LOCAL TEST RUNNER
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Initializing Zero-Touch GST LangGraph Orchestrator...\n")
    
    # We define our internal company books to feed into the graph
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

    # Execute the Graph autonomously!
    final_state = gst_app.invoke(initial_state)

    # Print the final results after the graph completes its run
    print("\n" + "="*50)
    print("🏁 GRAPH EXECUTION COMPLETE")
    print("="*50)
    print(f"Total Mismatches Found: {len(final_state['mismatches'])}")
    for m in final_state['mismatches']:
        print(f" - {m.invoice_number} | Issue: {m.issue_type}")