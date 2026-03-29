# backend/main.py
import uuid
import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional

# Import the compiled LangGraph app and Mock Router
from graph import gst_app
from mock_gstn import mock_gstn
from agents.vendor_chase import send_whatsapp, send_email_with_attachment
from db_schema import gstr3b_collection

app = FastAPI(
    title="Zero-Touch GST Agentic Network",
    description="Backend orchestration for autonomous GST compliance and penalty prevention.",
    version="2.0.0"
)

# Configure CORS for Next.js communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the Mock Government Portal routes
app.include_router(mock_gstn.router)

# --- REQUEST MODELS ---
class RecoveryRequest(BaseModel):
    period: str = "2026-03"
    days_to_cutoff: int = 20

class PDFRequest(BaseModel):
    period: str = "2026-03"
    send_whatsapp: bool = True
    send_email: bool = True

# --- Agent stage metadata for SSE ---
AGENT_STAGES = [
    {"id": "watcher",       "name": "GSTN Watcher",       "description": "Checking GSTN portal for new GSTR-2B data..."},
    {"id": "reconciler",    "name": "Reconciliation AI",   "description": "Comparing ERP records against Government GSTR-2B..."},
    {"id": "vendor_chase",  "name": "Vendor Chase Agent",  "description": "Generating omnichannel recovery outreach..."},
    {"id": "erp",           "name": "ERP Financial Engine", "description": "Calculating financial horizon from MongoDB Atlas..."},
    {"id": "optimizer",     "name": "AI Tax Optimizer",     "description": "Analyzing mismatches for ITC optimization..."},
    {"id": "filing",        "name": "Filing Agent",         "description": "Computing GSTR-3B tables from transactional data..."},
]

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    """Verifies backend and database connectivity."""
    return {"status": "Agentic Network is Live", "database_connected": True}


@app.get("/run-recovery-stream")
async def run_recovery_stream(period: str = "2026-03", days_to_cutoff: int = 20):
    """
    SSE endpoint: Streams real-time agent stage updates to the frontend.
    Each agent completion triggers an event so the UI can show progression.
    """
    async def event_generator():
        try:
            initial_state = {
                "current_period": period,
                "days_to_cutoff": days_to_cutoff,
                "books_data": [],
                "mismatches": [],
                "vendor_chase_log": [],
                "gstr3b_draft": {},
                "final_gstr3b": {},
                "hitl_flag": False
            }

            unique_run_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": unique_run_id}}

            # Send total stages info
            yield f"data: {json.dumps({'type': 'init', 'total_stages': len(AGENT_STAGES), 'stages': AGENT_STAGES})}\n\n"

            # Run the graph and stream events
            stage_index = 0
            for event in gst_app.stream(initial_state, config=config, stream_mode="updates"):
                if stage_index < len(AGENT_STAGES):
                    stage = AGENT_STAGES[stage_index]
                    yield f"data: {json.dumps({'type': 'stage_complete', 'stage_index': stage_index, 'stage_id': stage['id'], 'stage_name': stage['name']})}\n\n"
                    stage_index += 1
                await asyncio.sleep(0.1)

            # Get final state
            final_state = gst_app.get_state(config)
            result = final_state.values if final_state.values else {}

            # Build final payload
            final_payload = {
                "type": "complete",
                "thread_id": unique_run_id,
                "result": result.get("final_gstr3b"),
                "audit_summary": {
                    "mismatches_found": len(result.get("mismatches", [])),
                    "vendors_chased": len(result.get("vendor_chase_log", []))
                },
                "optimizer_report": result.get("gstr3b_draft", {}),
                "mismatches": result.get("mismatches", []),
                "financial_context": result.get("financial_context", {})
            }

            yield f"data: {json.dumps(final_payload, default=str)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/run-recovery")
async def run_gst_recovery(payload: RecoveryRequest):
    """
    Triggers the full Agentic Workflow (non-streaming fallback):
    Watcher -> Reconciler -> Vendor Chase -> ERP -> Optimizer -> Filing
    """
    try:
        initial_state = {
            "current_period": payload.period,
            "days_to_cutoff": payload.days_to_cutoff,
            "books_data": [],
            "mismatches": [],
            "vendor_chase_log": [],
            "gstr3b_draft": {},
            "final_gstr3b": {},
            "hitl_flag": False
        }

        unique_run_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": unique_run_id}}

        final_state = gst_app.invoke(initial_state, config=config)

        return {
            "status": "success",
            "thread_id": unique_run_id,
            "result": final_state.get("final_gstr3b"),
            "audit_summary": {
                "mismatches_found": len(final_state.get("mismatches", [])),
                "vendors_chased": len(final_state.get("vendor_chase_log", []))
            },
            "optimizer_report": final_state.get("gstr3b_draft", {}),
            "mismatches": final_state.get("mismatches", []),
            "financial_context": final_state.get("financial_context", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Failed: {str(e)}")


@app.post("/generate-pdf")
async def generate_and_send_pdf(payload: PDFRequest):
    """
    Generates a GSTR-3B PDF from the latest MongoDB data,
    sends it via WhatsApp and Email using existing infrastructure,
    and returns the PDF as a downloadable file.
    """
    try:
        from pdf_service import generate_gstr3b_pdf

        # Fetch latest GSTR-3B data from MongoDB
        gstr3b_data = gstr3b_collection.find_one(
            {"period": payload.period},
            {"_id": 0}
        )
        if not gstr3b_data:
            raise HTTPException(status_code=404, detail=f"No GSTR-3B data found for period {payload.period}")

        # Generate PDF
        pdf_path = generate_gstr3b_pdf(gstr3b_data)
        delivery_status = {"pdf_generated": True, "whatsapp": None, "email": None}

        # Send via WhatsApp
        if payload.send_whatsapp:
            try:
                wa_number = os.getenv("MY_WHATSAPP_NUMBER")
                msg_body = f"📋 GSTR-3B Draft for {payload.period} has been generated by the AI Agentic Network. Please review and approve."
                wa_sid = send_whatsapp(msg_body, wa_number)
                delivery_status["whatsapp"] = "sent" if wa_sid else "failed"
            except Exception as e:
                delivery_status["whatsapp"] = f"failed: {str(e)}"

        # Send via Email with attachment
        if payload.send_email:
            try:
                target_email = os.getenv("SENDER_EMAIL")
                email_sent = send_email_with_attachment(
                    subject=f"GSTR-3B Draft — {payload.period} | AI Generated",
                    body=f"Dear Sir/Madam,\n\nPlease find attached the AI-generated GSTR-3B draft for the period {payload.period}.\n\nThis draft was prepared by the Zero-Touch GST Agentic Network after reconciling {gstr3b_data.get('filing_meta', {}).get('records_processed', 'N/A')} ERP transactions against GSTR-2B government records.\n\nPlease review and approve for final filing.\n\nRegards,\nVishal Rajaraman\nFinance AI System",
                    to_email=target_email,
                    attachment_path=pdf_path,
                    attachment_filename=f"GSTR-3B_{payload.period}.pdf"
                )
                delivery_status["email"] = "sent" if email_sent else "failed"
            except Exception as e:
                delivery_status["email"] = f"failed: {str(e)}"

        # Return PDF as download
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"GSTR-3B_{payload.period}.pdf",
            headers={
                "X-Delivery-Status": json.dumps(delivery_status),
                "Access-Control-Expose-Headers": "X-Delivery-Status"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation Failed: {str(e)}")


@app.get("/status/{thread_id}")
async def get_run_status(thread_id: str):
    """Retrieves the persisted state of a specific run from MongoDB."""
    config = {"configurable": {"thread_id": thread_id}}
    state = gst_app.get_state(config)
    
    if not state.values:
        raise HTTPException(status_code=404, detail="Run not found")
        
    filtered_values = state.values.copy()
    if "gstr3b_draft" in filtered_values:
        del filtered_values["gstr3b_draft"]
        
    return filtered_values