'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Loader2, ServerCrash, BrainCircuit, ShieldAlert, ArrowRight, CheckSquare, Check, Scale, TrendingDown, Zap } from 'lucide-react';
import GSTR3BTable from './GSTR3BTable';
import { FinancialContext, OptimizerReport, AgentStage, GSTR3BData } from '../types/types';

/* ─── Design tokens ────────────────────────────────────────────────────────── */
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

  :root {
    --bg:        #0a0c10;
    --surface:   #10141c;
    --border:    #1e2535;
    --border-hi: #2e3a50;
    --gold:      #f0a500;
    --gold-dim:  #7a5210;
    --gold-glow: rgba(240,165,0,0.12);
    --red:       #e05555;
    --red-dim:   #3d1616;
    --red-glow:  rgba(224,85,85,0.10);
    --blue:      #4a8cff;
    --blue-dim:  #0e1e40;
    --green:     #34c97a;
    --green-dim: rgba(52,201,122,0.10);
    --text:      #e8ecf4;
    --muted:     #5a6478;
    --muted-hi:  #8292ae;
    --font-display: 'Syne', sans-serif;
    --font-mono:    'DM Mono', monospace;
  }

  .rd-root * { box-sizing: border-box; margin: 0; padding: 0; }

  .rd-root {
    min-height: 100vh;
    background: var(--bg);
    background-image:
      linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    font-family: var(--font-display);
    color: var(--text);
    padding: 40px 32px 160px;
  }

  .rd-inner { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 40px; }

  /* ── Header ── */
  .rd-header {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 36px 40px;
    overflow: hidden;
  }
  .rd-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, var(--gold-glow) 0%, transparent 60%);
    pointer-events: none;
  }
  .rd-header-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
  }
  .rd-header-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--gold-glow);
    border: 1px solid var(--gold-dim);
    color: var(--gold);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    margin-bottom: 16px;
    font-family: var(--font-mono);
  }
  .rd-header-tag .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
    animation: pulse-dot 2s infinite;
  }
  @keyframes pulse-dot {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(0.7); }
  }
  .rd-header h1 {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
    line-height: 1.1;
  }
  .rd-header p {
    margin-top: 8px;
    font-size: 14px;
    color: var(--muted-hi);
    font-family: var(--font-mono);
    font-weight: 300;
  }
  .rd-header-icon {
    position: absolute;
    right: 40px; top: 50%;
    transform: translateY(-50%);
    color: var(--gold-dim);
    opacity: 0.5;
  }

  /* ── Section labels ── */
  .rd-section-label {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: var(--font-mono);
    margin-bottom: 4px;
  }
  .rd-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  .rd-section-sub {
    font-size: 13px;
    color: var(--muted);
    font-family: var(--font-mono);
    font-weight: 300;
    margin-bottom: 20px;
  }

  /* ── Claim cards ── */
  .rd-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s, transform 0.15s;
    display: flex;
    align-items: flex-start;
    gap: 16px;
  }
  .rd-card:hover {
    border-color: var(--border-hi);
    transform: translateY(-1px);
  }
  .rd-card.selected {
    border-color: var(--gold);
    background: linear-gradient(135deg, rgba(240,165,0,0.06) 0%, var(--surface) 100%);
    box-shadow: 0 0 0 1px var(--gold-dim), 0 8px 32px rgba(240,165,0,0.08);
  }
  .rd-card-check {
    margin-top: 2px;
    flex-shrink: 0;
    color: var(--border-hi);
    transition: color 0.2s;
  }
  .rd-card.selected .rd-card-check { color: var(--gold); }

  .rd-card-body { flex: 1; }

  .rd-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }
  .rd-inv-id {
    font-size: 13px;
    font-family: var(--font-mono);
    font-weight: 500;
    color: var(--muted-hi);
    letter-spacing: 0.04em;
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 3px 8px;
    border-radius: 4px;
  }
  .rd-card.selected .rd-inv-id {
    border-color: var(--gold-dim);
    color: var(--gold);
  }
  .rd-itc-value {
    font-size: 22px;
    font-weight: 700;
    font-family: var(--font-mono);
    color: var(--muted);
    letter-spacing: -0.02em;
    transition: color 0.2s;
  }
  .rd-card.selected .rd-itc-value { color: var(--gold); }

  .rd-justification {
    background: var(--bg);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border-hi);
    border-radius: 6px;
    padding: 12px 14px;
    transition: border-left-color 0.2s;
  }
  .rd-card.selected .rd-justification { border-left-color: var(--gold-dim); }
  .rd-just-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: var(--font-mono);
    margin-bottom: 6px;
  }
  .rd-card.selected .rd-just-label { color: var(--gold); }
  .rd-just-text {
    font-size: 13px;
    line-height: 1.65;
    color: var(--muted-hi);
  }

  /* ── Impact breakdown mini card ── */
  .rd-impact-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 10px;
  }
  .rd-impact-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 10px;
  }
  .rd-impact-label {
    font-size: 9px;
    font-family: var(--font-mono);
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 3px;
  }
  .rd-impact-value {
    font-size: 14px;
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--text);
  }
  .rd-impact-value.savings { color: var(--green); }
  .rd-impact-value.liability { color: var(--gold); }

  /* ── Legal tags ── */
  .rd-legal-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
  }
  .rd-legal-tag {
    font-size: 9px;
    font-family: var(--font-mono);
    font-weight: 500;
    color: var(--blue);
    background: var(--blue-dim);
    border: 1px solid rgba(74,140,255,0.2);
    padding: 2px 7px;
    border-radius: 3px;
    letter-spacing: 0.04em;
  }

  /* ── Defer cards ── */
  .rd-defer-section { opacity: 0.9; }
  .rd-defer-card {
    background: var(--red-dim);
    border: 1px solid rgba(224,85,85,0.2);
    border-radius: 12px;
    padding: 20px 24px;
    transition: border-color 0.2s;
  }
  .rd-defer-card:hover { border-color: rgba(224,85,85,0.4); }
  .rd-defer-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  .rd-defer-id {
    font-size: 13px;
    font-family: var(--font-mono);
    font-weight: 500;
    color: var(--red);
    letter-spacing: 0.04em;
  }
  .rd-defer-val {
    font-size: 18px;
    font-weight: 700;
    font-family: var(--font-mono);
    color: var(--red);
    letter-spacing: -0.02em;
  }
  .rd-risk-box {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(224,85,85,0.15);
    border-radius: 6px;
    padding: 10px 14px;
  }
  .rd-risk-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--red);
    font-family: var(--font-mono);
    margin-bottom: 5px;
    opacity: 0.8;
  }
  .rd-risk-text {
    font-size: 13px;
    line-height: 1.65;
    color: #c98484;
  }
  .rd-risk-score {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 10px;
    font-family: var(--font-mono);
    font-weight: 600;
    color: var(--red);
    background: rgba(224,85,85,0.12);
    border: 1px solid rgba(224,85,85,0.25);
    padding: 3px 8px;
    border-radius: 4px;
  }

  /* ── Floating bar ── */
  .rd-fab {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(10,12,16,0.85);
    backdrop-filter: blur(24px);
    border-top: 1px solid var(--border-hi);
    padding: 20px 32px;
    z-index: 50;
  }
  .rd-fab-inner {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .rd-fab-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: var(--font-mono);
    margin-bottom: 4px;
  }
  .rd-fab-amount {
    font-size: 28px;
    font-weight: 700;
    font-family: var(--font-mono);
    letter-spacing: -0.03em;
    color: var(--gold);
  }
  .rd-fab-amount.zero { color: var(--muted); }
  .rd-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--gold);
    color: #000;
    border: none;
    border-radius: 10px;
    padding: 14px 28px;
    font-family: var(--font-display);
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    letter-spacing: 0.01em;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
    box-shadow: 0 4px 24px rgba(240,165,0,0.25);
  }
  .rd-btn:hover {
    background: #ffc229;
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(240,165,0,0.35);
  }
  .rd-btn:active { transform: translateY(0); }

  /* ── Loading / Error ── */
  .rd-center {
    min-height: 100vh;
    background: var(--bg);
    background-image:
      linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    font-family: var(--font-display);
    color: var(--text);
  }
  .rd-center p { color: var(--muted-hi); font-family: var(--font-mono); font-size: 14px; }
  .rd-center h2 { font-size: 20px; font-weight: 700; color: var(--text); }

  /* ── Stage Stepper ── */
  .rd-stages {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 32px;
    width: 440px;
    max-width: 90vw;
  }
  .rd-stage {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 20px;
    position: relative;
    transition: opacity 0.4s;
  }
  .rd-stage::before {
    content: '';
    position: absolute;
    left: 32px;
    top: 42px;
    bottom: -14px;
    width: 2px;
    background: var(--border);
    transition: background 0.4s;
  }
  .rd-stage:last-child::before { display: none; }
  .rd-stage.completed::before { background: var(--gold-dim); }
  .rd-stage.active::before { background: var(--gold); animation: pulse-line 1.5s infinite; }

  @keyframes pulse-line {
    0%,100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .rd-stage-icon {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 2px solid var(--border);
    background: var(--bg);
    transition: all 0.4s;
    position: relative;
    z-index: 2;
  }
  .rd-stage.completed .rd-stage-icon {
    border-color: var(--gold);
    background: var(--gold);
  }
  .rd-stage.active .rd-stage-icon {
    border-color: var(--gold);
    background: var(--gold-glow);
    box-shadow: 0 0 16px rgba(240,165,0,0.4);
  }
  .rd-stage-num {
    font-size: 10px;
    font-family: var(--font-mono);
    font-weight: 600;
    color: var(--muted);
  }
  .rd-stage.completed .rd-stage-num { color: #000; }
  .rd-stage.active .rd-stage-num { color: var(--gold); }

  .rd-stage-info { flex: 1; }
  .rd-stage-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--muted);
    transition: color 0.3s;
  }
  .rd-stage.completed .rd-stage-name { color: var(--text); }
  .rd-stage.active .rd-stage-name { color: var(--gold); }

  .rd-stage-desc {
    font-size: 11px;
    font-family: var(--font-mono);
    font-weight: 300;
    color: var(--muted);
    margin-top: 2px;
    transition: color 0.3s;
  }
  .rd-stage.active .rd-stage-desc { color: var(--muted-hi); }
  .rd-stage.completed .rd-stage-desc { color: var(--muted-hi); }

  .rd-stage-check {
    color: var(--muted);
    transition: color 0.3s, opacity 0.3s;
    opacity: 0;
  }
  .rd-stage.completed .rd-stage-check { color: var(--green); opacity: 1; }

  @keyframes spin { to { transform: rotate(360deg); } }
`;

const DEFAULT_STAGES: AgentStage[] = [
  { id: "watcher",      name: "GSTN Watcher",        description: "Checking GSTN portal for new GSTR-2B data..." },
  { id: "reconciler",   name: "Reconciliation AI",    description: "Comparing ERP records against Government GSTR-2B..." },
  { id: "vendor_chase", name: "Vendor Chase Agent",   description: "Generating omnichannel recovery outreach..." },
  { id: "erp",          name: "ERP Financial Engine",  description: "Calculating financial horizon from MongoDB..." },
  { id: "optimizer",    name: "AI Tax Optimizer",      description: "Analyzing mismatches for ITC optimization..." },
  { id: "filing",       name: "Filing Agent",          description: "Computing GSTR-3B from transactional data..." },
];

export default function RecoveryDashboard() {
  const [step, setStep] = useState<1 | 2>(1);
  const [selectedInvoices, setSelectedInvoices] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<OptimizerReport | null>(null);
  const [context, setContext] = useState<FinancialContext | null>(null);
  const [gstr3bData, setGstr3bData] = useState<GSTR3BData | null>(null);

  // Stage progression state
  const [stages, setStages] = useState<AgentStage[]>(DEFAULT_STAGES);
  const [currentStageIndex, setCurrentStageIndex] = useState(-1);
  const [completedStages, setCompletedStages] = useState<Set<number>>(new Set());

  useEffect(() => {
    const fetchWithSSE = () => {
      try {
        const evtSource = new EventSource('http://localhost:8000/run-recovery-stream?period=2026-03&days_to_cutoff=20');

        evtSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'init') {
              setStages(data.stages || DEFAULT_STAGES);
              setCurrentStageIndex(0);
            } else if (data.type === 'stage_complete') {
              setCompletedStages(prev => new Set([...prev, data.stage_index]));
              setCurrentStageIndex(data.stage_index + 1);
            } else if (data.type === 'complete') {
              evtSource.close();
              setReport(data.optimizer_report || null);
              setGstr3bData(data.result || null);
              setContext({
                current_output_tax: data.financial_context?.current_output_tax || 0,
                safe_itc: data.financial_context?.total_validated_itc || 0,
                ledger_balance: 50000
              });
              setIsLoading(false);
            } else if (data.type === 'error') {
              evtSource.close();
              setError(data.message);
              setIsLoading(false);
            }
          } catch (parseError) {
            console.error('SSE parse error:', parseError);
          }
        };

        evtSource.onerror = () => {
          evtSource.close();
          // Fallback to regular POST
          fetchFallback();
        };
      } catch {
        fetchFallback();
      }
    };

    const fetchFallback = async () => {
      try {
        const response = await fetch('http://localhost:8000/run-recovery', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ period: "2026-03", days_to_cutoff: 20 })
        });
        if (!response.ok) throw new Error("Failed to connect to Agentic Network");
        const data = await response.json();
        setReport(data.optimizer_report || null);
        setGstr3bData(data.result || null);
        setContext({
          current_output_tax: data.financial_context?.current_output_tax || 0,
          safe_itc: data.financial_context?.total_validated_itc || 0,
          ledger_balance: 50000
        });
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWithSSE();
  }, []);

  const parseITCValue = (val: string | number) => {
    if (typeof val === 'number') return val;
    return parseFloat(String(val).replace(/[^\d.-]/g, '')) || 0;
  };

  const handleToggle = (inv: string) => {
    const newSet = new Set(selectedInvoices);
    if (newSet.has(inv)) newSet.delete(inv); else newSet.add(inv);
    setSelectedInvoices(newSet);
  };

  const fmt = (n: number) => '₹' + n.toLocaleString('en-IN', { maximumFractionDigits: 2 });

  if (isLoading) return (
    <>
      <style>{css}</style>
      <div className="rd-center">
        <Loader2 style={{ width: 40, height: 40, color: 'var(--gold)', animation: 'spin 1s linear infinite' }} />

        {/* Stage Stepper */}
        <div className="rd-stages">
          {stages.map((stage, i) => {
            const isCompleted = completedStages.has(i);
            const isActive = i === currentStageIndex;
            const stateClass = isCompleted ? 'completed' : isActive ? 'active' : '';

            return (
              <div key={stage.id} className={`rd-stage ${stateClass}`}>
                <div className="rd-stage-icon">
                  {isCompleted ? (
                    <Check style={{ width: 14, height: 14, color: '#000' }} />
                  ) : isActive ? (
                    <Loader2 style={{ width: 14, height: 14, color: 'var(--gold)', animation: 'spin 1s linear infinite' }} />
                  ) : (
                    <span className="rd-stage-num">{i + 1}</span>
                  )}
                </div>
                <div className="rd-stage-info">
                  <div className="rd-stage-name">{stage.name}</div>
                  <div className="rd-stage-desc">{stage.description}</div>
                </div>
                <Check className="rd-stage-check" style={{ width: 16, height: 16 }} />
              </div>
            );
          })}
        </div>
      </div>
    </>
  );

  if (error || !context || !report) return (
    <>
      <style>{css}</style>
      <div className="rd-center">
        <ServerCrash style={{ width: 40, height: 40, color: 'var(--red)' }} />
        <h2>Analysis Failed</h2>
        <p>{error || "No report generated."}</p>
      </div>
    </>
  );

  const manuallyClaimedItc = (report.recommended_to_claim || [])
    .filter(rec => selectedInvoices.has(rec.invoice_number))
    .reduce((sum, rec) => sum + parseITCValue(rec.itc_value), 0);

  // Auto-send PDF when generating GSTR-3B
  const handleGenerate = () => {
    setStep(2);
    // Fire-and-forget: generate PDF and send via WhatsApp + Email
    fetch('http://localhost:8000/generate-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ period: '2026-03', send_whatsapp: true, send_email: true })
    }).then(res => {
      if (res.ok) return res.blob();
      throw new Error('PDF failed');
    }).then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'GSTR-3B_2026-03.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }).catch(err => console.error('PDF delivery error:', err));
  };

  if (step === 2) {
    if (!gstr3bData) {
      return (
        <>
          <style>{css}</style>
          <div className="rd-center">
            <Loader2 style={{ width: 40, height: 40, color: 'var(--gold)', animation: 'spin 1s linear infinite' }} />
            <p>Generating GSTR-3B and sending PDF...</p>
          </div>
        </>
      );
    }
    return (
      <GSTR3BTable
        gstr3bData={gstr3bData}
        manuallyClaimedItc={manuallyClaimedItc}
        onBack={() => setStep(1)}
      />
    );
  }

  return (
    <>
      <style>{css}</style>
      <div className="rd-root">
        <div className="rd-inner">

          {/* Header */}
          <div className="rd-header">
            <div className="rd-header-accent" />
            <div className="rd-header-tag">
              <span className="dot" />
              Live Analysis
            </div>
            <h1>Quantitative AI<br />Optimizer Report</h1>
            <p>Deep analysis of invoice mismatches and recovery strategies</p>
            <div className="rd-header-icon">
              <BrainCircuit style={{ width: 72, height: 72 }} />
            </div>
          </div>

          {/* Claim section */}
          <div>
            <div className="rd-section-label">Safe to Claim — AI Recommended</div>
            <p className="rd-section-sub">
              Select invoices to bridge your cash gap · AI-validated legal justification
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {(report.recommended_to_claim || []).map((rec) => {
                const sel = selectedInvoices.has(rec.invoice_number);
                const impact = rec.impact_breakdown;
                return (
                  <div
                    key={rec.invoice_number}
                    className={`rd-card${sel ? ' selected' : ''}`}
                    onClick={() => handleToggle(rec.invoice_number)}
                  >
                    <CheckSquare className="rd-card-check" style={{ width: 20, height: 20 }} />
                    <div className="rd-card-body">
                      <div className="rd-card-top">
                        <span className="rd-inv-id">{rec.invoice_number}</span>
                        <span className="rd-itc-value">{fmt(parseITCValue(rec.itc_value))}</span>
                      </div>
                      <div className="rd-justification">
                        <div className="rd-just-label">AI Justification</div>
                        <p className="rd-just-text">{rec.financial_justification}</p>

                        {/* Impact Breakdown */}
                        {impact && (
                          <div className="rd-impact-grid">
                            <div className="rd-impact-item">
                              <div className="rd-impact-label">Current Liability</div>
                              <div className="rd-impact-value liability">{fmt(impact.current_liability)}</div>
                            </div>
                            <div className="rd-impact-item">
                              <div className="rd-impact-label">After Claim</div>
                              <div className="rd-impact-value liability">{fmt(impact.after_claim)}</div>
                            </div>
                            <div className="rd-impact-item">
                              <div className="rd-impact-label">Cash Saved</div>
                              <div className="rd-impact-value savings">{fmt(impact.cash_saved)}</div>
                            </div>
                            <div className="rd-impact-item">
                              <div className="rd-impact-label">GSTN Variance</div>
                              <div className="rd-impact-value" style={{ fontSize: 12 }}>{impact.variance_from_gstn}</div>
                            </div>
                          </div>
                        )}

                        {/* Legal Section Tags */}
                        {rec.legal_sections && rec.legal_sections.length > 0 && (
                          <div className="rd-legal-tags">
                            <Scale style={{ width: 10, height: 10, color: 'var(--blue)', opacity: 0.6 }} />
                            {rec.legal_sections.map((sec, i) => (
                              <span key={i} className="rd-legal-tag">{sec}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Defer section */}
          {(report.recommended_to_defer || []).length > 0 && (
            <div className="rd-defer-section">
              <div className="rd-section-label" style={{ color: 'var(--red)', opacity: 0.7 }}>
                <ShieldAlert style={{ width: 14, height: 14 }} />
                High Risk — Recommended for Deferral
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 16 }}>
                {report.recommended_to_defer.map((rec) => (
                  <div key={rec.invoice_number} className="rd-defer-card">
                    <div className="rd-defer-top">
                      <span className="rd-defer-id">{rec.invoice_number}</span>
                      <span className="rd-defer-val">{fmt(parseITCValue(rec.itc_value))}</span>
                    </div>
                    <div className="rd-risk-box">
                      <div className="rd-risk-label">Risk Assessment</div>
                      <p className="rd-risk-text">{rec.risk_assessment}</p>
                      {rec.risk_score && (
                        <div className="rd-risk-score">
                          <TrendingDown style={{ width: 10, height: 10 }} />
                          Risk Score: {rec.risk_score}/10
                        </div>
                      )}
                      {rec.legal_sections && rec.legal_sections.length > 0 && (
                        <div className="rd-legal-tags" style={{ marginTop: 8 }}>
                          <Scale style={{ width: 10, height: 10, color: 'var(--red)', opacity: 0.6 }} />
                          {rec.legal_sections.map((sec, i) => (
                            <span key={i} className="rd-legal-tag" style={{ color: 'var(--red)', background: 'var(--red-glow)', borderColor: 'rgba(224,85,85,0.25)' }}>{sec}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Floating action bar */}
        <div className="rd-fab">
          <div className="rd-fab-inner">
            <div>
              <div className="rd-fab-label">Selected Additional ITC</div>
              <div className={`rd-fab-amount${manuallyClaimedItc === 0 ? ' zero' : ''}`}>
                {fmt(manuallyClaimedItc)}
              </div>
            </div>
            <button className="rd-btn" onClick={handleGenerate}>
              Generate Final GSTR-3B
              <ArrowRight style={{ width: 18, height: 18 }} />
            </button>
          </div>
        </div>

      </div>
    </>
  );
}