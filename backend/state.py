# backend/state.py
from typing import TypedDict, List, Dict, Annotated
import operator
from pydantic import BaseModel

# --- Data Models ---
class Invoice(BaseModel):
    invoice_number: str
    vendor_gstin: str
    date: str
    amount: float
    tax_amount: float
    type: str
    status: str = "filed"

class MismatchRecord(BaseModel):
    invoice_number: str
    vendor_gstin: str
    issue_type: str 
    tax_value: float
    is_critical: bool 

class ITCRecommendation(BaseModel):
    invoice_number: str
    action: str 
    reasoning: str
    financial_impact: float

# --- The Graph State ---
class GSTGraphState(TypedDict):
    current_period: str                          
    days_to_cutoff: int                          
    
    # Raw Data
    books_data: List[Dict]                    
    gstr2a_live_data: List[Dict]              
    gstr2b_static_data: List[Dict]            
    
    # Agent Outputs (Annotated allows parallel agents to append data safely)
    mismatches: Annotated[List[MismatchRecord], operator.add]     
    vendor_chase_log: Annotated[List[Dict], operator.add]         
    itc_recommendations: Annotated[List[ITCRecommendation], operator.add]
    
    # --- NEW: ERP Financial Horizon ---
    financial_context: Dict  # <--- This is what the ERP Agent feeds to the Optimizer
    
    # Final Outputs
    gstr3b_draft: Dict                           
    final_gstr3b: Dict
    hitl_flag: bool                              
    workflow_status: str