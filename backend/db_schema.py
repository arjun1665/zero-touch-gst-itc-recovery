import os
import csv
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Load your .env variables
load_dotenv()

# 2. Setup MongoDB Connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["zero_touch_gst"]

# 3. Define Collections (These were causing your NameError)
audit_collection = db["audit_logs"]
erp_collection = db["erp_inventory"]
gstr3b_collection = db["gstr3b_records"]

# --- HELPER FUNCTIONS ---

def log_audit(agent_name, action, details):
    """Stores a permanent audit trail for the hackathon demo."""
    audit_entry = {
        "timestamp": datetime.now(),
        "agent": agent_name,
        "action": action,
        "details": details
    }
    audit_collection.insert_one(audit_entry)
    print(f"📑 [Audit] Logged {action} for {agent_name}")

def safe_float(value, default=0.0):
    if value is None: return default
    stripped = str(value).strip().upper()
    if stripped in ("", "FALSE", "TRUE", "N/A", "NONE"): return default
    try:
        return float(stripped)
    except ValueError:
        return default

# --- MAIN MIGRATION FUNCTION ---

def sync_csv_to_mongo(filepath="erp_register.csv"):
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return
    
    records = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["Taxable_Value"] = safe_float(row.get("Taxable_Value"))
            row["IGST"] = safe_float(row.get("IGST"))
            row["CGST"] = safe_float(row.get("CGST"))
            row["SGST"] = safe_float(row.get("SGST"))
            
            row["Goods_Received"] = str(row.get("Goods_Received", "FALSE")).strip().upper() == "TRUE"
            row["Is_RCM"] = str(row.get("Is_RCM", "FALSE")).strip().upper() == "TRUE"
            records.append(row)
            
    if records:
        erp_collection.delete_many({})
        erp_collection.insert_many(records)
        log_audit("Database_Manager", "ERP_Sync", f"Injected {len(records)} records.")
        print(f"✅ Successfully migrated {len(records)} records to MongoDB.")