# backend/seed_db.py
from db_schema import sync_csv_to_mongo
import os

if __name__ == "__main__":
    print("📂 Starting Data Migration: CSV -> MongoDB...")
    
    # Ensure the path points to your actual register file
    csv_file = "erp_register.csv"
    
    if os.path.exists(csv_file):
        sync_csv_to_mongo(csv_file)
        print("✅ Migration Successful! ERP records are now in 'erp_inventory' collection.")
        print("📑 Audit log created in 'audit_logs' collection.")
    else:
        print(f"❌ Error: {csv_file} not found. Please check the file path.")