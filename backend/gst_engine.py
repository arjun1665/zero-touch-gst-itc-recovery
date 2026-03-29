from datetime import datetime

class EnterpriseGSTEngine:
    """Processes transactions from MongoDB seeded data to build tax liability timeline."""
    
    def safe_float(self, value):
        """Safely converts string/None to float, returning 0.0 for non-numeric data."""
        if value is None:
            return 0.0
        try:
            # Handle potential currency symbols or commas in the seeded data
            clean_val = str(value).replace('₹', '').replace(',', '').strip().upper()
            if clean_val in ["FALSE", "TRUE", "NA", "", "NONE"]:
                return 0.0
            return float(clean_val)
        except ValueError:
            return 0.0

    def process_erp_data(self, records: list, current_month: int, current_year: int) -> dict:
        print(f"⚙️ [GST Engine] Ingesting {len(records)} records from MongoDB Atlas...")
        
        current_output_tax = 0.0
        accrued_next_month_tax = 0.0
        processed_records = 0
        total_books_itc = 0.0

        # Iterating through MongoDB records list instead of CSV file
        for row in records:
            processed_records += 1
            
            igst = self.safe_float(row.get('IGST', 0))
            cgst = self.safe_float(row.get('CGST', 0))
            sgst = self.safe_float(row.get('SGST', 0))
            
            total_tax = igst + cgst + sgst
            
            is_rcm = str(row.get('Is_RCM', "FALSE")).strip().upper() == "TRUE"
            doc_type = str(row.get('Document_Type', "Invoice")).strip().title()
            trans_type = str(row.get('Transaction_Type', "Sale")).strip().title()
            
            if doc_type == "Credit_Note":
                total_tax = -abs(total_tax)
                
            try:
                # Expecting Date format "YYYY-MM-DD" in Mongo
                inv_date = datetime.strptime(row['Date'], "%Y-%m-%d")
            except (ValueError, KeyError):
                continue 

            # --- 1. Output Tax Calculation (Sales + Purchases under RCM) ---
            if trans_type == "Sale" or is_rcm:
                if inv_date.year == current_year and inv_date.month == current_month:
                    current_output_tax += total_tax
                # Accrued liability logic (handle December to January rollover)
                elif (inv_date.year == current_year and inv_date.month == current_month + 1) or \
                     (current_month == 12 and inv_date.month == 1 and inv_date.year == current_year + 1):
                    if inv_date.day <= 20:
                        accrued_next_month_tax += total_tax

            # --- 2. Input Tax Credit (Purchases) ---
            if trans_type == "Purchase" and not is_rcm:
                if inv_date.year == current_year and inv_date.month == current_month:
                    total_books_itc += total_tax

        return {
            "records_processed": processed_records,
            "current_output_tax": round(current_output_tax, 2),
            "accrued_next_month_tax": round(accrued_next_month_tax, 2),
            "total_books_itc": round(total_books_itc, 2)
        }

    def generate_financial_context(self, engine_summary: dict, total_validated_itc: float) -> dict:
        total_liability_horizon = engine_summary["current_output_tax"] + engine_summary["accrued_next_month_tax"]
        net_tax_payable_current = max(0, engine_summary["current_output_tax"] - total_validated_itc)

        return {
            "current_output_tax": engine_summary["current_output_tax"],
            "accrued_next_month_tax": engine_summary["accrued_next_month_tax"],
            "total_liability_horizon": round(total_liability_horizon, 2),
            "total_validated_itc": round(total_validated_itc, 2),
            "net_tax_payable_current": round(net_tax_payable_current, 2),
            "strategy_indicator": "HIGH_CASH_REQUIRED" if total_liability_horizon > (total_validated_itc * 1.5) else "STABLE"
        }