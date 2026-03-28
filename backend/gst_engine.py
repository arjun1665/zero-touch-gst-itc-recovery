import csv
from datetime import datetime

class EnterpriseGSTEngine:
    """Reads transactions from the unified ERP CSV and builds the tax liability timeline."""
    
    def safe_float(self, value):
        """Safely converts string to float, returning 0.0 for non-numeric data."""
        if value is None:
            return 0.0
        try:
            # Strip whitespace and handle empty strings or 'FALSE'/'TRUE'
            clean_val = str(value).strip().upper()
            if clean_val in ["FALSE", "TRUE", "NA", "", "NONE"]:
                return 0.0
            return float(clean_val)
        except ValueError:
            return 0.0

    def process_erp_csv(self, filepath: str, current_month: int, current_year: int) -> dict:
        print(f"⚙️ [GST Engine] Ingesting raw ERP data from {filepath}...")
        
        current_output_tax = 0.0
        accrued_next_month_tax = 0.0
        processed_records = 0
        total_books_itc = 0.0

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                processed_records += 1
                
                # USE SAFE_FLOAT to prevent 'FALSE' conversion errors
                igst = self.safe_float(row.get('IGST', 0))
                cgst = self.safe_float(row.get('CGST', 0))
                sgst = self.safe_float(row.get('SGST', 0))
                
                total_tax = igst + cgst + sgst
                
                is_rcm = str(row.get('Is_RCM', "FALSE")).strip().upper() == "TRUE"
                doc_type = str(row.get('Document_Type', "Invoice")).strip().title()
                trans_type = str(row.get('Transaction_Type', "Sale")).strip().title()
                
                # Handle Credit Notes
                if doc_type == "Credit_Note":
                    total_tax = -abs(total_tax)
                    
                try:
                    inv_date = datetime.strptime(row['Date'], "%Y-%m-%d")
                except (ValueError, KeyError):
                    continue # Skip rows with invalid dates

                # --- 1. Output Tax Calculation (Sales + Purchases under RCM) ---
                if trans_type == "Sale" or is_rcm:
                    if inv_date.year == current_year and inv_date.month == current_month:
                        current_output_tax += total_tax
                    elif inv_date.year == current_year and inv_date.month == current_month + 1 and inv_date.day <= 20:
                        accrued_next_month_tax += total_tax

                # --- 2. Input Tax Credit (Purchases) ---
                if trans_type == "Purchase" and not is_rcm:
                    # We only consider it for current month if it's a purchase
                    if inv_date.year == current_year and inv_date.month == current_month:
                        total_books_itc += total_tax

        return {
            "records_processed": processed_records,
            "current_output_tax": current_output_tax,
            "accrued_next_month_tax": accrued_next_month_tax,
            "total_books_itc": total_books_itc
        }

    def generate_financial_context(self, engine_summary: dict, total_validated_itc: float) -> dict:
        total_liability_horizon = engine_summary["current_output_tax"] + engine_summary["accrued_next_month_tax"]
        net_tax_payable_current = max(0, engine_summary["current_output_tax"] - total_validated_itc)

        return {
            "current_output_tax": engine_summary["current_output_tax"],
            "accrued_next_month_tax": engine_summary["accrued_next_month_tax"],
            "total_liability_horizon": total_liability_horizon,
            "total_validated_itc": total_validated_itc,
            "net_tax_payable_current": net_tax_payable_current,
            "strategy_indicator": "HIGH_CASH_REQUIRED" if total_liability_horizon > (total_validated_itc * 1.5) else "STABLE"
        }