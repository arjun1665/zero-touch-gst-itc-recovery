export interface FinancialContext {
  current_output_tax: number;
  safe_itc: number;
  ledger_balance: number;
}

export interface ImpactBreakdown {
  current_liability: number;
  after_claim: number;
  cash_saved: number;
  variance_from_gstn: string;
}

export interface Recommendation {
  invoice_number: string;
  itc_value: string | number;
  financial_justification?: string;
  risk_assessment?: string;
  legal_sections?: string[];
  impact_breakdown?: ImpactBreakdown;
  risk_score?: number;
}

export interface OptimizerReport {
  mismatch_analysis: any[];
  recommended_to_claim: Recommendation[];
  recommended_to_defer: Recommendation[];
}

export interface AgentStage {
  id: string;
  name: string;
  description: string;
}

// Full GSTR-3B computed data structure from the filing agent
export interface GSTR3BData {
  period: string;
  generated_at: string;
  tables: {
    "3_1": {
      a: { taxable_value: number; igst: number; cgst: number; sgst: number; cess: number };
      b: { taxable_value: number; igst: number; cess: number };
      c: { taxable_value: number };
      d: { taxable_value: number; igst: number; cgst: number; sgst: number; cess: number };
      e: { taxable_value: number };
    };
    "3_2": {
      unregistered: { taxable_value: number; igst: number };
      composition: { taxable_value: number; igst: number };
      uin_holders: { taxable_value: number; igst: number };
    };
    "4_ITC": {
      "4_A": {
        import_goods: { igst: number };
        import_services: { igst: number };
        rcm: { igst: number; cgst: number; sgst: number };
        isd: { igst: number; cgst: number; sgst: number };
        all_other_itc: { igst: number; cgst: number; sgst: number };
        total: { igst: number; cgst: number; sgst: number };
      };
      "4_B_Reversed": {
        rule_42_43: { igst: number; cgst: number; sgst: number };
        others: { igst: number; cgst: number; sgst: number };
      };
      "4_C_Net_ITC": { igst: number; cgst: number; sgst: number };
      "4_D_Ineligible": {
        sec_17_5: { igst: number; cgst: number; sgst: number };
        others: { igst: number; cgst: number; sgst: number };
      };
    };
    "5_Exempt": {
      exempt_nil: { inter: number; intra: number };
      non_gst: { inter: number; intra: number };
    };
    "5_1_Interest": {
      interest: { igst: number; cgst: number; sgst: number; cess: number };
      late_fee: { cgst: number; sgst: number };
    };
    "6_1_Payment": {
      igst: { payable: number; itc_igst: number; itc_cgst: number; itc_sgst: number; cash: number };
      cgst: { payable: number; itc_igst: number; itc_cgst: number; itc_sgst: number; cash: number };
      sgst: { payable: number; itc_igst: number; itc_cgst: number; itc_sgst: number; cash: number };
      cess: { payable: number; itc_igst: number; itc_cgst: number; itc_sgst: number; cash: number };
      total_payable: number;
      ledger_balance: number;
      top_up_required: number;
    };
  };
  filing_meta: {
    due_date: string;
    filing_status: string;
    records_processed: number;
    sales_count: number;
    purchase_count: number;
  };
}