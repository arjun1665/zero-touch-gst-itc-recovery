# backend/pdf_service.py
"""
Generates GSTR-3B PDF using reportlab from the computed MongoDB data.
Pure Python — no browser or external dependency needed.
"""
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def fmt(val, fallback="—"):
    """Format number as Indian currency string."""
    if val is None or val == 0:
        return fallback
    return f"Rs.{val:,.2f}"


def generate_gstr3b_pdf(gstr3b_data: dict) -> str:
    """
    Generates a GSTR-3B PDF matching the official form layout.
    Returns the path to the generated PDF file.
    """
    period = gstr3b_data.get("period", "2026-03")
    tables = gstr3b_data.get("tables", {})
    meta = gstr3b_data.get("filing_meta", {})

    # Create temp file
    pdf_dir = os.path.join(tempfile.gettempdir(), "gstr3b_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"GSTR-3B_{period}.pdf")

    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DocTitle', fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name='DocSubtitle', fontSize=10, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.grey, spaceAfter=12))
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=11, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6, textColor=colors.HexColor('#1a1a2e')))
    styles.add(ParagraphStyle(name='MetaLabel', fontSize=8, fontName='Helvetica', textColor=colors.grey))
    styles.add(ParagraphStyle(name='MetaValue', fontSize=9, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='FooterNote', fontSize=7, fontName='Helvetica-Oblique', textColor=colors.grey, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CellText', fontSize=8, fontName='Helvetica', leading=10))

    elements = []

    # ─── Header ───
    elements.append(Paragraph("FORM GSTR-3B", styles['DocTitle']))
    elements.append(Paragraph(f"Monthly Summary Return · Period: {period}", styles['DocSubtitle']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e8b830'), spaceAfter=8))

    # ─── Meta Info ───
    meta_data = [
        ["GSTIN", "Legal Name", "Filing Period", "Status"],
        ["29AADCB2230M1Z3", "Demo Enterprises Pvt Ltd", f"{period}", meta.get('filing_status', 'DRAFT')]
    ]
    meta_table = Table(meta_data, colWidths=[120, 160, 100, 120])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('TOPPADDING', (0, 1), (-1, 1), 2),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # ─── Helper to build data tables ───
    header_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

    # ─── Section 3.1 ───
    t31 = tables.get("3_1", {})
    elements.append(Paragraph("3.1 – Details of Outward Supplies and Inward Supplies Liable to Reverse Charge", styles['SectionTitle']))
    t31_data = [
        ["Nature of Supplies", "Taxable Value (Rs.)", "IGST (Rs.)", "CGST (Rs.)", "SGST (Rs.)", "Cess (Rs.)"],
        ["(a) Outward taxable supplies", fmt(t31.get("a", {}).get("taxable_value")), fmt(t31.get("a", {}).get("igst")), fmt(t31.get("a", {}).get("cgst")), fmt(t31.get("a", {}).get("sgst")), "—"],
        ["(b) Zero rated supplies", fmt(t31.get("b", {}).get("taxable_value")), fmt(t31.get("b", {}).get("igst")), "N/A", "N/A", "—"],
        ["(c) Nil rated, exempted", fmt(t31.get("c", {}).get("taxable_value")), "N/A", "N/A", "N/A", "N/A"],
        ["(d) Inward (reverse charge)", fmt(t31.get("d", {}).get("taxable_value")), fmt(t31.get("d", {}).get("igst")), fmt(t31.get("d", {}).get("cgst")), fmt(t31.get("d", {}).get("sgst")), "—"],
        ["(e) Non-GST supplies", fmt(t31.get("e", {}).get("taxable_value")), "N/A", "N/A", "N/A", "N/A"],
    ]
    t31_table = Table(t31_data, colWidths=[160, 80, 72, 72, 72, 50])
    t31_table.setStyle(header_style)
    elements.append(t31_table)
    elements.append(Spacer(1, 10))

    # ─── Section 3.2 ───
    t32 = tables.get("3_2", {})
    elements.append(Paragraph("3.2 – Inter-State Supplies to Unregistered, Composition & UIN Holders", styles['SectionTitle']))
    t32_data = [
        ["Place of Supply", "Total Taxable Value (Rs.)", "IGST (Rs.)"],
        ["Unregistered Persons", fmt(t32.get("unregistered", {}).get("taxable_value")), fmt(t32.get("unregistered", {}).get("igst"))],
        ["Composition Taxable Persons", fmt(t32.get("composition", {}).get("taxable_value")), fmt(t32.get("composition", {}).get("igst"))],
        ["UIN Holders", fmt(t32.get("uin_holders", {}).get("taxable_value")), fmt(t32.get("uin_holders", {}).get("igst"))],
    ]
    t32_table = Table(t32_data, colWidths=[200, 150, 150])
    t32_table.setStyle(header_style)
    elements.append(t32_table)
    elements.append(Spacer(1, 10))

    # ─── Section 4 ───
    t4 = tables.get("4_ITC", {})
    t4a = t4.get("4_A", {})
    t4b = t4.get("4_B_Reversed", {})
    t4c = t4.get("4_C_Net_ITC", {})
    t4d = t4.get("4_D_Ineligible", {})

    elements.append(Paragraph("4 – Eligible ITC", styles['SectionTitle']))
    t4_data = [
        ["Details", "IGST (Rs.)", "CGST (Rs.)", "SGST (Rs.)", "Cess (Rs.)"],
        ["(A) ITC Available", "", "", "", ""],
        ["  (1) Import of goods", fmt(t4a.get("import_goods", {}).get("igst")), "N/A", "N/A", "—"],
        ["  (2) Import of services", fmt(t4a.get("import_services", {}).get("igst")), "N/A", "N/A", "—"],
        ["  (3) Inward (reverse charge)", fmt(t4a.get("rcm", {}).get("igst")), fmt(t4a.get("rcm", {}).get("cgst")), fmt(t4a.get("rcm", {}).get("sgst")), "—"],
        ["  (4) Inward from ISD", "—", "—", "—", "—"],
        ["  (5) All other ITC", fmt(t4a.get("all_other_itc", {}).get("igst")), fmt(t4a.get("all_other_itc", {}).get("cgst")), fmt(t4a.get("all_other_itc", {}).get("sgst")), "—"],
        ["(B) ITC Reversed", "", "", "", ""],
        ["  (1) Rules 38, 42, 43 / Sec 17(5)", fmt(t4b.get("rule_42_43", {}).get("igst")), fmt(t4b.get("rule_42_43", {}).get("cgst")), fmt(t4b.get("rule_42_43", {}).get("sgst")), "—"],
        ["  (2) Others", "—", "—", "—", "—"],
        ["(C) Net ITC Available", fmt(t4c.get("igst")), fmt(t4c.get("cgst")), fmt(t4c.get("sgst")), "—"],
        ["(D) Ineligible ITC", "", "", "", ""],
        ["  (1) As per Section 17(5)", fmt(t4d.get("sec_17_5", {}).get("igst")), fmt(t4d.get("sec_17_5", {}).get("cgst")), fmt(t4d.get("sec_17_5", {}).get("sgst")), "—"],
        ["  (2) Others", "—", "—", "—", "—"],
    ]
    t4_table = Table(t4_data, colWidths=[180, 80, 80, 80, 50])
    t4_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Section subheaders
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 7), (0, 7), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 11), (0, 11), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 11), (-1, 11), colors.HexColor('#f0f0f0')),
        # Net ITC row highlight
        ('FONTNAME', (0, 10), (-1, 10), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor('#fff8e1')),
    ])
    t4_table.setStyle(t4_style)
    elements.append(t4_table)
    elements.append(Spacer(1, 10))

    # ─── Section 5 ───
    t5 = tables.get("5_Exempt", {})
    elements.append(Paragraph("5 – Exempt, Nil-Rated and Non-GST Inward Supplies", styles['SectionTitle']))
    t5_data = [
        ["Nature of Supplies", "Inter-State (Rs.)", "Intra-State (Rs.)"],
        ["Exempt and nil-rated", fmt(t5.get("exempt_nil", {}).get("inter")), fmt(t5.get("exempt_nil", {}).get("intra"))],
        ["Non-GST supply", fmt(t5.get("non_gst", {}).get("inter")), fmt(t5.get("non_gst", {}).get("intra"))],
    ]
    t5_table = Table(t5_data, colWidths=[220, 140, 140])
    t5_table.setStyle(header_style)
    elements.append(t5_table)
    elements.append(Spacer(1, 10))

    # ─── Section 5.1 ───
    t51 = tables.get("5_1_Interest", {})
    elements.append(Paragraph("5.1 – Interest and Late Fee Payable", styles['SectionTitle']))
    t51_data = [
        ["Description", "IGST (Rs.)", "CGST (Rs.)", "SGST (Rs.)", "Cess (Rs.)"],
        ["Interest", fmt(t51.get("interest", {}).get("igst")), fmt(t51.get("interest", {}).get("cgst")), fmt(t51.get("interest", {}).get("sgst")), "—"],
        ["Late Fee", "N/A", fmt(t51.get("late_fee", {}).get("cgst")), fmt(t51.get("late_fee", {}).get("sgst")), "N/A"],
    ]
    t51_table = Table(t51_data, colWidths=[140, 90, 90, 90, 60])
    t51_table.setStyle(header_style)
    elements.append(t51_table)
    elements.append(Spacer(1, 10))

    # ─── Section 6.1 ───
    t6 = tables.get("6_1_Payment", {})
    elements.append(Paragraph("6.1 – Payment of Tax", styles['SectionTitle']))
    t6_data = [
        ["Description", "Tax Payable", "ITC–IGST", "ITC–CGST", "ITC–SGST", "ITC–Cess", "Cash", "Interest", "Late Fee"],
        ["Integrated Tax", fmt(t6.get("igst", {}).get("payable")), fmt(t6.get("igst", {}).get("itc_igst")), "—", "—", "—", fmt(t6.get("igst", {}).get("cash")), "—", "—"],
        ["Central Tax", fmt(t6.get("cgst", {}).get("payable")), "—", fmt(t6.get("cgst", {}).get("itc_cgst")), "—", "—", fmt(t6.get("cgst", {}).get("cash")), "—", "—"],
        ["State/UT Tax", fmt(t6.get("sgst", {}).get("payable")), "—", "—", fmt(t6.get("sgst", {}).get("itc_sgst")), "—", fmt(t6.get("sgst", {}).get("cash")), "—", "—"],
        ["Cess", "—", "—", "—", "—", "—", "—", "—", "—"],
    ]
    t6_table = Table(t6_data, colWidths=[70, 55, 55, 55, 55, 48, 55, 48, 48])
    t6_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    t6_table.setStyle(t6_style)
    elements.append(t6_table)
    elements.append(Spacer(1, 16))

    # ─── Summary Footer ───
    total_payable = t6.get("total_payable", 0)

    summary_data = [
        ["Total Tax Payable", fmt(total_payable), "Due Date", meta.get("due_date", "—")],
    ]
    summary_table = Table(summary_data, colWidths=[150, 150, 100, 100])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e8b830')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8b830')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8e1')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"Generated by Zero-Touch GST Agentic Network · {datetime.now().strftime('%d %b %Y %H:%M')} · AI Draft — Pending Approval",
        styles['FooterNote']
    ))

    doc.build(elements)
    print(f"📄 PDF generated: {pdf_path}")
    return pdf_path
