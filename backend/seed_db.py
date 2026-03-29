# backend/seed_db.py
# Seeds the MongoDB erp_inventory with comprehensive GST transaction data
# including Supply_Type, Recipient_Type, Import_Type fields needed for GSTR-3B

import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from db_schema import erp_collection, log_audit, safe_float

load_dotenv()

def seed_comprehensive_data():
    """
    Injects comprehensive ERP transactions into MongoDB.
    Includes all field types needed for full GSTR-3B computation:
      - Supply_Type: taxable / zero_rated / nil_rated / exempted / non_gst
      - Recipient_Type: registered / unregistered / composition / uin_holder
      - Import_Type: goods / services / (blank for domestic)
    """
    records = [
        # ─── SALES (Outward Supplies) ───
        # Regular taxable sales — Intra-state (CGST+SGST)
        {
            "Invoice_Number": "SALE-2026-001", "Date": "2026-03-01",
            "Party_Name": "Alpha Traders Pvt Ltd", "GSTIN": "29AADCA1234B1Z1",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 500000, "IGST": 0, "CGST": 45000, "SGST": 45000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        {
            "Invoice_Number": "SALE-2026-002", "Date": "2026-03-05",
            "Party_Name": "Beta Distributors", "GSTIN": "29BBDCB5678C1Z2",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 320000, "IGST": 0, "CGST": 28800, "SGST": 28800,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # Regular taxable sale — Inter-state (IGST)
        {
            "Invoice_Number": "SALE-2026-003", "Date": "2026-03-08",
            "Party_Name": "Gamma Industries", "GSTIN": "27CCDCC9012D1Z3",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 450000, "IGST": 81000, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # Inter-state sale to unregistered person (for Table 3.2)
        {
            "Invoice_Number": "SALE-2026-004", "Date": "2026-03-10",
            "Party_Name": "Cash Customer - Delhi", "GSTIN": "",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 75000, "IGST": 13500, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "unregistered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # Sale to composition dealer (for Table 3.2)
        {
            "Invoice_Number": "SALE-2026-005", "Date": "2026-03-12",
            "Party_Name": "Small Mart Composition", "GSTIN": "07DDDCD3456E1Z4",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 40000, "IGST": 7200, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "composition",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # Nil-rated sale
        {
            "Invoice_Number": "SALE-2026-006", "Date": "2026-03-15",
            "Party_Name": "Rural Agri Supplies", "GSTIN": "33EEECE7890F1Z5",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 85000, "IGST": 0, "CGST": 0, "SGST": 0,
            "Supply_Type": "nil_rated", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },

        # ─── PURCHASES (Inward Supplies) ───
        # Regular domestic purchase — Intra-state
        {
            "Invoice_Number": "INV-2026-001", "Date": "2026-03-02",
            "Party_Name": "Acme Supplies Pvt Ltd", "GSTIN": "27AADCB2230M1Z2",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 277777, "IGST": 0, "CGST": 25000, "SGST": 25000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Regular domestic purchase — Inter-state
        {
            "Invoice_Number": "INV-2026-045", "Date": "2026-03-05",
            "Party_Name": "TechParts Global", "GSTIN": "29BBBCB1120K1Z5",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 66666, "IGST": 12000, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase with VALUE MISMATCH (Vendor filed ₹8500 instead of actual)
        {
            "Invoice_Number": "INV-2026-088", "Date": "2026-03-07",
            "Party_Name": "ValueParts Inc", "GSTIN": "07CCDCB3340L1Z8",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 47222, "IGST": 8500, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — Vendor DID NOT FILE (missing from GSTR-2B)
        {
            "Invoice_Number": "INV-2026-102", "Date": "2026-03-06",
            "Party_Name": "Missing Vendor Co", "GSTIN": "24DDDCB4450M1Z1",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 120000, "IGST": 21600, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — eligible inter-state
        {
            "Invoice_Number": "INV-2026-115", "Date": "2026-03-04",
            "Party_Name": "Delta Tech Solutions", "GSTIN": "33EEECB5560Q1Z3",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 27777, "IGST": 5000, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — Goods NOT received (ITC Block under Section 16)
        {
            "Invoice_Number": "INV-2026-130", "Date": "2026-03-09",
            "Party_Name": "Slow Delivery Corp", "GSTIN": "29FFFCB6670R1Z6",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 55000, "IGST": 0, "CGST": 4950, "SGST": 4950,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": False, "Import_Type": ""
        },
        # Purchase — Blocked under Section 17(5) (e.g., club membership)
        {
            "Invoice_Number": "INV-2026-140", "Date": "2026-03-11",
            "Party_Name": "Premium Club Services", "GSTIN": "29GGGCB7780S1Z7",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 200000, "IGST": 0, "CGST": 18000, "SGST": 18000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Blocked_Sec17_5", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase under RCM — Legal services (Table 3.1d)
        {
            "Invoice_Number": "INV-2026-150", "Date": "2026-03-02",
            "Party_Name": "Taj Legal Associates", "GSTIN": "27TAJ1234Z5",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 50000, "IGST": 0, "CGST": 4500, "SGST": 4500,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": True, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Another RCM purchase — GTA services
        {
            "Invoice_Number": "INV-2026-155", "Date": "2026-03-14",
            "Party_Name": "FastFreight GTA", "GSTIN": "29HHHCB8890T1Z8",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 30000, "IGST": 5400, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": True, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — intra-state matched
        {
            "Invoice_Number": "INV-2026-200", "Date": "2026-03-04",
            "Party_Name": "Sharma Electronics", "GSTIN": "27SHARMA1234Z5",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 100000, "IGST": 0, "CGST": 9000, "SGST": 9000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Import of Goods (for Table 4A1)
        {
            "Invoice_Number": "IMP-2026-001", "Date": "2026-03-06",
            "Party_Name": "Shanghai Components Ltd", "GSTIN": "",
            "Transaction_Type": "Purchase", "Document_Type": "Bill of Entry",
            "Taxable_Value": 180000, "IGST": 32400, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": "goods"
        },
        # Import of Services (for Table 4A2) 
        {
            "Invoice_Number": "IMP-2026-002", "Date": "2026-03-13",
            "Party_Name": "AWS Cloud Services", "GSTIN": "",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 95000, "IGST": 17100, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": "services"
        },
        # Exempt/Nil-rated inward supply (for Table 5)
        {
            "Invoice_Number": "INV-2026-250", "Date": "2026-03-08",
            "Party_Name": "Organic Farm Fresh", "GSTIN": "29JJJCB0012V1Z0",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 45000, "IGST": 0, "CGST": 0, "SGST": 0,
            "Supply_Type": "nil_rated", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # Non-GST inward supply (for Table 5)
        {
            "Invoice_Number": "INV-2026-260", "Date": "2026-03-10",
            "Party_Name": "Petrol Station", "GSTIN": "29KKKFUEL123Z1",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 60000, "IGST": 0, "CGST": 0, "SGST": 0,
            "Supply_Type": "non_gst", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
    ]

    # Clear existing and insert fresh
    erp_collection.delete_many({})
    erp_collection.insert_many(records)
    log_audit("Database_Manager", "COMPREHENSIVE_SEED", f"Injected {len(records)} records with full GSTR-3B fields.")
    print(f"✅ Successfully seeded {len(records)} comprehensive ERP records to MongoDB.")
    return len(records)


if __name__ == "__main__":
    print("📂 Starting Comprehensive Data Seed: → MongoDB...")
    count = seed_comprehensive_data()
    print(f"✅ Seed Successful! {count} ERP records now in 'erp_inventory' collection.")
    print("📑 Audit log created in 'audit_logs' collection.")