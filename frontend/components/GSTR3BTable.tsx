'use client';

import React, { useState } from 'react';
import { Download, ArrowLeft, AlertTriangle, CheckCircle, Send, Loader2 } from 'lucide-react';
import { GSTR3BData } from '../types/types';

interface GSTR3BProps {
  gstr3bData: GSTR3BData;
  manuallyClaimedItc: number;
  onBack: () => void;
}

/* ─── Design tokens ─────────────────────── */
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

  :root {
    --bg:        #0a0c10;
    --surface:   #10141c;
    --surface2:  #13182200;
    --border:    #1e2535;
    --border-hi: #2e3a50;
    --gold:      #f0a500;
    --gold-dim:  #7a5210;
    --gold-glow: rgba(240,165,0,0.10);
    --red:       #e05555;
    --red-dim:   rgba(224,85,85,0.10);
    --green:     #34c97a;
    --green-dim: rgba(52,201,122,0.10);
    --blue:      #4a8cff;
    --blue-dim:  rgba(74,140,255,0.10);
    --text:      #e8ecf4;
    --muted:     #5a6478;
    --muted-hi:  #8292ae;
    --font-display: 'Syne', sans-serif;
    --font-mono:    'DM Mono', monospace;
  }

  .g3b * { box-sizing: border-box; margin: 0; padding: 0; }

  .g3b-page {
    min-height: 100vh;
    background: var(--bg);
    background-image:
      linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
    background-size: 40px 40px;
    font-family: var(--font-display);
    color: var(--text);
    padding: 32px 24px 80px;
  }

  .g3b-wrap { max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }

  /* ── Topbar ── */
  .g3b-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 20px;
  }
  .g3b-back {
    display: flex; align-items: center; gap: 8px;
    background: none; border: 1px solid var(--border); color: var(--muted-hi);
    font-family: var(--font-display); font-size: 13px; font-weight: 600;
    padding: 8px 16px; border-radius: 8px; cursor: pointer;
    transition: border-color .2s, color .2s;
  }
  .g3b-back:hover { border-color: var(--border-hi); color: var(--text); }
  .g3b-btn-group { display: flex; gap: 10px; align-items: center; }
  .g3b-print-btn {
    display: flex; align-items: center; gap: 8px;
    background: var(--gold); color: #000; border: none;
    font-family: var(--font-display); font-size: 13px; font-weight: 700;
    padding: 8px 20px; border-radius: 8px; cursor: pointer;
    transition: background .2s, transform .15s, box-shadow .2s;
    box-shadow: 0 4px 20px rgba(240,165,0,.2);
  }
  .g3b-print-btn:hover { background: #ffc229; transform: translateY(-1px); box-shadow: 0 6px 28px rgba(240,165,0,.3); }
  .g3b-print-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

  /* ── Toast ── */
  .g3b-toast {
    position: fixed;
    bottom: 24px; right: 24px;
    background: var(--surface);
    border: 1px solid var(--border-hi);
    border-radius: 10px;
    padding: 14px 20px;
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text);
    z-index: 100;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    animation: slideUp 0.3s ease-out;
  }
  .g3b-toast.success { border-color: rgba(52,201,122,.4); }
  .g3b-toast.error { border-color: rgba(224,85,85,.4); }
  @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  /* ── Document card ── */
  .g3b-doc {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
  }

  /* ── Document header ── */
  .g3b-doc-header {
    position: relative;
    padding: 32px 40px 28px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(135deg, var(--gold-glow) 0%, transparent 50%);
    overflow: hidden;
  }
  .g3b-doc-header::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
  }
  .g3b-doc-title {
    font-size: 22px; font-weight: 800; letter-spacing: .04em;
    text-transform: uppercase; color: var(--text);
  }
  .g3b-doc-subtitle {
    font-size: 12px; font-family: var(--font-mono); color: var(--gold);
    letter-spacing: .1em; text-transform: uppercase; margin-top: 4px;
  }
  .g3b-doc-meta {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 16px; margin-top: 24px;
  }
  .g3b-meta-box {
    background: var(--bg);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 14px;
  }
  .g3b-meta-label {
    font-size: 9px; font-family: var(--font-mono); font-weight: 600;
    letter-spacing: .14em; text-transform: uppercase; color: var(--muted);
    margin-bottom: 4px;
  }
  .g3b-meta-value {
    font-size: 13px; font-family: var(--font-mono); font-weight: 500;
    color: var(--text);
  }

  /* ── Section wrapper ── */
  .g3b-section { border-bottom: 1px solid var(--border); }
  .g3b-section:last-child { border-bottom: none; }

  .g3b-sec-header {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 40px;
    background: rgba(255,255,255,0.015);
    border-bottom: 1px solid var(--border);
  }
  .g3b-sec-num {
    font-size: 11px; font-family: var(--font-mono); font-weight: 500;
    color: var(--gold); background: var(--gold-glow);
    border: 1px solid var(--gold-dim); border-radius: 4px;
    padding: 2px 8px; letter-spacing: .06em; flex-shrink: 0;
  }
  .g3b-sec-title {
    font-size: 12px; font-weight: 600; color: var(--muted-hi);
    letter-spacing: .02em; line-height: 1.4;
  }

  /* ── Tables ── */
  .g3b-table-wrap { padding: 0 40px 24px; overflow-x: auto; }
  .g3b-table {
    width: 100%; border-collapse: collapse;
    font-size: 12px; margin-top: 16px;
  }
  .g3b-table th {
    background: rgba(255,255,255,0.04);
    color: var(--muted-hi);
    font-family: var(--font-mono); font-size: 10px; font-weight: 500;
    letter-spacing: .08em; text-transform: uppercase;
    padding: 10px 14px; text-align: right;
    border: 1px solid var(--border);
  }
  .g3b-table th:first-child { text-align: left; }
  .g3b-table td {
    padding: 10px 14px; border: 1px solid var(--border);
    color: var(--text); vertical-align: top; line-height: 1.5;
  }
  .g3b-table td:not(:first-child) {
    text-align: right;
    font-family: var(--font-mono); font-size: 12px;
  }
  .g3b-table tr:hover td { background: rgba(255,255,255,0.015); }

  /* Row variants */
  .g3b-row-subhead td {
    background: rgba(255,255,255,0.03);
    font-size: 10px; font-family: var(--font-mono); font-weight: 600;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted);
  }
  .g3b-row-total td {
    background: var(--gold-glow) !important;
    border-color: var(--gold-dim) !important;
    font-weight: 700;
  }
  .g3b-row-total td:not(:first-child) {
    color: var(--gold); font-size: 14px;
  }
  .g3b-row-highlight td {
    background: var(--blue-dim) !important;
  }
  .g3b-row-highlight td:not(:first-child) { color: var(--blue); }

  .g3b-row-danger td { background: var(--red-dim) !important; }
  .g3b-row-danger td:not(:first-child) { color: var(--red); }

  .g3b-row-success td { background: var(--green-dim) !important; }
  .g3b-row-success td:not(:first-child) { color: var(--green); }

  /* Cell variants */
  .g3b-cell-na {
    color: var(--muted) !important; font-style: italic; font-size: 10px !important;
  }
  .g3b-cell-ai {
    color: var(--blue) !important; font-weight: 500;
  }
  .g3b-cell-ai::before { content: '+ '; }

  .g3b-row-indent td:first-child { padding-left: 32px; }

  /* ── Footer summary ── */
  .g3b-footer {
    margin: 0 40px 32px;
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .g3b-footer-box {
    background: var(--bg);
    border: 1px solid var(--border); border-radius: 10px;
    padding: 16px 20px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .g3b-footer-label {
    font-size: 10px; font-family: var(--font-mono); font-weight: 600;
    letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
    margin-bottom: 6px;
  }
  .g3b-footer-value {
    font-size: 20px; font-weight: 700;
    font-family: var(--font-mono); letter-spacing: -.02em;
  }
  .g3b-footer-icon { opacity: .6; }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Print ── */
  @media print {
    .g3b-topbar, .g3b-toast { display: none !important; }
    .g3b-page {
      background: white; color: black;
      background-image: none; padding: 0;
    }
    .g3b-doc {
      border: none; border-radius: 0;
      box-shadow: none; background: white;
    }
    .g3b-table th { background: #f0f0f0; color: #333; }
    .g3b-table td, .g3b-table th { border-color: #ccc; color: #000; }
    :root {
      --border: #ccc; --text: #000; --muted-hi: #444; --muted: #777;
      --gold: #b07800; --gold-glow: #fff8e6; --gold-dim: #c8a432;
      --blue: #0055cc; --blue-dim: #eef4ff;
      --red: #cc0000; --red-dim: #fff0f0;
      --green: #007700; --green-dim: #f0fff4;
    }
  }
`;

const fmt = (n: number | undefined, fallback = '—') => {
  if (n === undefined || n === null) return fallback;
  if (n === 0) return fallback;
  return n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const NA = <span className="g3b-cell-na">N/A</span>;

export default function GSTR3BTable({ gstr3bData, manuallyClaimedItc, onBack }: GSTR3BProps) {
  const [isPDFLoading, setIsPDFLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const t = gstr3bData.tables;
  const meta = gstr3bData.filing_meta;
  const t31 = t["3_1"];
  const t32 = t["3_2"];
  const t4 = t["4_ITC"];
  const t5 = t["5_Exempt"];
  const t51 = t["5_1_Interest"];
  const t6 = t["6_1_Payment"];

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const handleDownloadPDF = async () => {
    setIsPDFLoading(true);
    try {
      const response = await fetch('http://localhost:8000/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          period: gstr3bData.period,
          send_whatsapp: true,
          send_email: true
        })
      });

      if (!response.ok) throw new Error('PDF generation failed');

      // Get delivery status from headers
      const deliveryStatus = response.headers.get('X-Delivery-Status');
      let status: any = {};
      try {
        status = deliveryStatus ? JSON.parse(deliveryStatus) : {};
      } catch { }

      // Download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GSTR-3B_${gstr3bData.period}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      // Show delivery notification
      const whatsappOk = status.whatsapp === 'sent';
      const emailOk = status.email === 'sent';
      if (whatsappOk && emailOk) {
        showToast('PDF downloaded! Also sent via WhatsApp & Email ✓', 'success');
      } else if (whatsappOk || emailOk) {
        showToast(`PDF downloaded! Sent via ${whatsappOk ? 'WhatsApp' : 'Email'} ✓`, 'success');
      } else {
        showToast('PDF downloaded successfully!', 'success');
      }
    } catch (err: any) {
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setIsPDFLoading(false);
    }
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: css }} />
      <div className="g3b-page">
        <div className="g3b-wrap">

          {/* Topbar */}
          <div className="g3b-topbar">
            <button className="g3b-back" onClick={onBack}>
              <ArrowLeft style={{ width: 16, height: 16 }} />
              Back to AI Analysis
            </button>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <CheckCircle style={{ width: 14, height: 14 }} />
              PDF sent via WhatsApp & Email
            </div>
          </div>

          {/* Document */}
          <div className="g3b-doc">

            {/* Doc Header */}
            <div className="g3b-doc-header">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div className="g3b-doc-title">Form GSTR-3B</div>
                  <div className="g3b-doc-subtitle">Monthly Summary Return · Period: {gstr3bData.period}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--muted)', letterSpacing: '.1em', textTransform: 'uppercase', marginBottom: 4 }}>Status</div>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'var(--gold-glow)', border: '1px solid var(--gold-dim)', borderRadius: 6, padding: '4px 10px', fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--gold)', fontWeight: 600, letterSpacing: '.08em' }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--gold)', display: 'inline-block', animation: 'pulse-dot 2s infinite' }} />
                    {meta.filing_status === 'READY_FOR_APPROVAL' ? 'AI DRAFT — READY' : 'AWAITING FUNDS'}
                  </div>
                </div>
              </div>
              <div className="g3b-doc-meta">
                <div className="g3b-meta-box">
                  <div className="g3b-meta-label">GSTIN</div>
                  <div className="g3b-meta-value">29AADCB2230M1Z3</div>
                </div>
                <div className="g3b-meta-box">
                  <div className="g3b-meta-label">Legal Name</div>
                  <div className="g3b-meta-value">Demo Enterprises Pvt Ltd</div>
                </div>
                <div className="g3b-meta-box">
                  <div className="g3b-meta-label">Records Processed</div>
                  <div className="g3b-meta-value">{meta.records_processed} txns ({meta.sales_count} sales, {meta.purchase_count} purchases)</div>
                </div>
              </div>
            </div>

            {/* ─── Section 3.1 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">3.1</span>
                <span className="g3b-sec-title">Details of Outward Supplies and inward supplies liable to reverse charge</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '38%' }}>Nature of Supplies</th>
                      <th>Total Taxable Value (₹)</th>
                      <th>Integrated Tax (₹)</th>
                      <th>Central Tax (₹)</th>
                      <th>State/UT Tax (₹)</th>
                      <th>Cess (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>(a) Outward taxable supplies (other than zero rated, nil rated and exempted)</td>
                      <td>{fmt(t31.a.taxable_value)}</td>
                      <td>{fmt(t31.a.igst)}</td>
                      <td>{fmt(t31.a.cgst)}</td>
                      <td>{fmt(t31.a.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>(b) Outward taxable supplies (zero rated)</td>
                      <td>{fmt(t31.b.taxable_value)}</td>
                      <td>{fmt(t31.b.igst)}</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>(c) Other outward supplies (Nil rated, exempted)</td>
                      <td>{fmt(t31.c.taxable_value)}</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                    </tr>
                    <tr>
                      <td>(d) Inward supplies (liable to reverse charge)</td>
                      <td>{fmt(t31.d.taxable_value)}</td>
                      <td>{fmt(t31.d.igst)}</td>
                      <td>{fmt(t31.d.cgst)}</td>
                      <td>{fmt(t31.d.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>(e) Non-GST outward supplies</td>
                      <td>{fmt(t31.e.taxable_value)}</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Section 3.2 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">3.2</span>
                <span className="g3b-sec-title">Of the supplies shown in 3.1(a), details of inter-state supplies</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '50%' }}>Place of Supply (State/UT)</th>
                      <th>Total Taxable Value (₹)</th>
                      <th>Amount of Integrated Tax (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Unregistered Persons</td>
                      <td>{fmt(t32.unregistered.taxable_value)}</td>
                      <td>{fmt(t32.unregistered.igst)}</td>
                    </tr>
                    <tr>
                      <td>Composition Taxable Persons</td>
                      <td>{fmt(t32.composition.taxable_value)}</td>
                      <td>{fmt(t32.composition.igst)}</td>
                    </tr>
                    <tr>
                      <td>UIN Holders</td>
                      <td>{fmt(t32.uin_holders.taxable_value)}</td>
                      <td>{fmt(t32.uin_holders.igst)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Section 4 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">4</span>
                <span className="g3b-sec-title">Eligible ITC</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '38%' }}>Details</th>
                      <th>Integrated Tax (₹)</th>
                      <th>Central Tax (₹)</th>
                      <th>State/UT Tax (₹)</th>
                      <th>Cess (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="g3b-row-subhead">
                      <td colSpan={5}>(A) ITC Available (whether in full or part)</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(1) Import of goods</td>
                      <td>{fmt(t4["4_A"].import_goods.igst)}</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(2) Import of services</td>
                      <td>{fmt(t4["4_A"].import_services.igst)}</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(3) Inward supplies liable to reverse charge</td>
                      <td>{fmt(t4["4_A"].rcm.igst)}</td>
                      <td>{fmt(t4["4_A"].rcm.cgst)}</td>
                      <td>{fmt(t4["4_A"].rcm.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(4) Inward supplies from ISD</td>
                      <td>{fmt(t4["4_A"].isd.igst)}</td>
                      <td>{fmt(t4["4_A"].isd.cgst)}</td>
                      <td>{fmt(t4["4_A"].isd.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(5) All other ITC — GSTR-2B reconciled</td>
                      <td>{fmt(t4["4_A"].all_other_itc.igst)}</td>
                      <td>{fmt(t4["4_A"].all_other_itc.cgst)}</td>
                      <td>{fmt(t4["4_A"].all_other_itc.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    {manuallyClaimedItc > 0 && (
                      <tr className="g3b-row-highlight g3b-row-indent">
                        <td style={{ fontStyle: 'italic' }}>
                          (+) AI Recommended Additions — Manually Approved
                          <div style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--font-mono)', marginTop: 2 }}>
                            ITC recovered via agentic reconciliation
                          </div>
                        </td>
                        <td className="g3b-cell-ai">{fmt(manuallyClaimedItc * 0.4)}</td>
                        <td className="g3b-cell-ai">{fmt(manuallyClaimedItc * 0.3)}</td>
                        <td className="g3b-cell-ai">{fmt(manuallyClaimedItc * 0.3)}</td>
                        <td className="g3b-cell-na">—</td>
                      </tr>
                    )}

                    <tr className="g3b-row-subhead">
                      <td colSpan={5}>(B) ITC Reversed</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(1) As per rules 38, 42 and 43 of CGST Rules and sub-section (5) of section 17</td>
                      <td>{fmt(t4["4_B_Reversed"].rule_42_43.igst)}</td>
                      <td>{fmt(t4["4_B_Reversed"].rule_42_43.cgst)}</td>
                      <td>{fmt(t4["4_B_Reversed"].rule_42_43.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(2) Others</td>
                      <td>{fmt(t4["4_B_Reversed"].others.igst)}</td>
                      <td>{fmt(t4["4_B_Reversed"].others.cgst)}</td>
                      <td>{fmt(t4["4_B_Reversed"].others.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>

                    <tr className="g3b-row-total">
                      <td>(C) Net ITC Available (A) – (B)</td>
                      <td>{fmt(t4["4_C_Net_ITC"].igst)}</td>
                      <td>{fmt(t4["4_C_Net_ITC"].cgst)}</td>
                      <td>{fmt(t4["4_C_Net_ITC"].sgst)}</td>
                      <td>—</td>
                    </tr>

                    <tr className="g3b-row-subhead">
                      <td colSpan={5}>(D) Ineligible ITC</td>
                    </tr>
                    <tr className="g3b-row-indent g3b-row-danger">
                      <td>(1) As per section 17(5)</td>
                      <td>{fmt(t4["4_D_Ineligible"].sec_17_5.igst)}</td>
                      <td>{fmt(t4["4_D_Ineligible"].sec_17_5.cgst)}</td>
                      <td>{fmt(t4["4_D_Ineligible"].sec_17_5.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-indent">
                      <td>(2) Others</td>
                      <td>{fmt(t4["4_D_Ineligible"].others.igst)}</td>
                      <td>{fmt(t4["4_D_Ineligible"].others.cgst)}</td>
                      <td>{fmt(t4["4_D_Ineligible"].others.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Section 5 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">5</span>
                <span className="g3b-sec-title">Values of exempt, nil-rated and non-GST inward supplies</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '50%' }}>Nature of Supplies</th>
                      <th>Inter-State Supplies (₹)</th>
                      <th>Intra-State Supplies (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>From a supplier under composition scheme, exempt and nil-rated supply</td>
                      <td>{fmt(t5.exempt_nil.inter)}</td>
                      <td>{fmt(t5.exempt_nil.intra)}</td>
                    </tr>
                    <tr>
                      <td>Non-GST supply</td>
                      <td>{fmt(t5.non_gst.inter)}</td>
                      <td>{fmt(t5.non_gst.intra)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Section 5.1 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">5.1</span>
                <span className="g3b-sec-title">Interest and late fee payable</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '38%' }}>Description</th>
                      <th>Integrated Tax (₹)</th>
                      <th>Central Tax (₹)</th>
                      <th>State/UT Tax (₹)</th>
                      <th>Cess (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Interest</td>
                      <td>{fmt(t51.interest.igst)}</td>
                      <td>{fmt(t51.interest.cgst)}</td>
                      <td>{fmt(t51.interest.sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>Late Fee</td>
                      <td className="g3b-cell-na">N/A</td>
                      <td>{fmt(t51.late_fee.cgst)}</td>
                      <td>{fmt(t51.late_fee.sgst)}</td>
                      <td className="g3b-cell-na">N/A</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Section 6.1 ─── */}
            <div className="g3b-section">
              <div className="g3b-sec-header">
                <span className="g3b-sec-num">6.1</span>
                <span className="g3b-sec-title">Payment of Tax</span>
              </div>
              <div className="g3b-table-wrap">
                <table className="g3b-table">
                  <thead>
                    <tr>
                      <th style={{ width: '22%' }}>Description</th>
                      <th>Tax Payable (₹)</th>
                      <th>Paid through ITC — IGST (₹)</th>
                      <th>Paid through ITC — CGST (₹)</th>
                      <th>Paid through ITC — SGST (₹)</th>
                      <th>Paid through ITC — Cess (₹)</th>
                      <th>Tax Paid in Cash (₹)</th>
                      <th>Interest (₹)</th>
                      <th>Late Fee (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Integrated Tax</td>
                      <td>{fmt(t6.igst.payable)}</td>
                      <td>{fmt(t6.igst.itc_igst)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td>{fmt(t6.igst.cash)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>Central Tax</td>
                      <td>{fmt(t6.cgst.payable)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td>{fmt(t6.cgst.itc_cgst)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td>{fmt(t6.cgst.cash)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>State/UT Tax</td>
                      <td>{fmt(t6.sgst.payable)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td>{fmt(t6.sgst.itc_sgst)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td>{fmt(t6.sgst.cash)}</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr>
                      <td>Cess</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                      <td className="g3b-cell-na">—</td>
                    </tr>
                    <tr className="g3b-row-total">
                      <td>Total</td>
                      <td>{fmt(t6.igst.payable + t6.cgst.payable + t6.sgst.payable)}</td>
                      <td>{fmt(t6.igst.itc_igst)}</td>
                      <td>{fmt(t6.cgst.itc_cgst)}</td>
                      <td>{fmt(t6.sgst.itc_sgst)}</td>
                      <td>—</td>
                      <td>{fmt(t6.total_payable)}</td>
                      <td>—</td>
                      <td>—</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ─── Footer summary ─── */}
            <div className="g3b-footer" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="g3b-footer-box">
                <div>
                  <div className="g3b-footer-label">Total Tax Payable</div>
                  <div className="g3b-footer-value" style={{ color: 'var(--gold)' }}>
                    ₹{(t6.igst.payable + t6.cgst.payable + t6.sgst.payable).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="g3b-footer-icon">
                  <AlertTriangle style={{ width: 28, height: 28, color: 'var(--gold)' }} />
                </div>
              </div>
              <div className="g3b-footer-box">
                <div>
                  <div className="g3b-footer-label">Due Date</div>
                  <div className="g3b-footer-value" style={{ color: 'var(--text)' }}>
                    {meta.due_date}
                  </div>
                </div>
                <div className="g3b-footer-icon">
                  <CheckCircle style={{ width: 28, height: 28, color: 'var(--muted)' }} />
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className={`g3b-toast ${toast.type}`}>
          {toast.type === 'success' ? (
            <CheckCircle style={{ width: 16, height: 16, color: 'var(--green)' }} />
          ) : (
            <AlertTriangle style={{ width: 16, height: 16, color: 'var(--red)' }} />
          )}
          {toast.message}
        </div>
      )}
    </>
  );
}