import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class PDFGenerator:
    """
    Utility class to generate clean, professional PDF reports 
    for Construction Intelligence Hub analysis results.
    """
    
    @staticmethod
    def generate_report(data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Define Custom Color Palette (Apple / Dark Blue & Purple aesthetic in PDF print styling)
        primary_color = colors.HexColor("#1A2B49") # Dark Navy
        secondary_color = colors.HexColor("#4D39E9") # Premium Violet
        accent_color = colors.HexColor("#00B4D8") # Light Blue
        text_color = colors.HexColor("#2B2D42") # Off-Black
        light_bg = colors.HexColor("#F8F9FA") # Light Grey for rows
        
        # Modify existing styles or add new ones
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=28,
            textColor=primary_color,
            alignment=0, # Left aligned
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=11,
            leading=14,
            textColor=secondary_color,
            spaceAfter=25
        )
        
        h1_style = ParagraphStyle(
            'DocH1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=primary_color,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            'DocH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=secondary_color,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_color,
            spaceAfter=8
        )
        
        bullet_style = ParagraphStyle(
            'DocBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_color,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=6
        )

        # Header Logo/Title block
        story.append(Paragraph("🏗️ Construction Intelligence Hub", title_style))
        story.append(Paragraph("AI-Powered Smart Construction Planning & Space Optimization", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Executive Summary
        story.append(Paragraph("1. Our Recommendation", h1_style))
        cost_lakhs = data['estimated_cost'] / 100000
        summary_text = (
            f"Based on your plot size and family needs, the best house type for you is a "
            f"<b>{data['suitable_type']}</b>. Our AI is <b>{data['confidence']}% confident</b> "
            f"in this recommendation based on your inputs."
        )
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 10))
        
        # Primary Parameters Table
        story.append(Paragraph("2. Plot & Cost Details", h1_style))
        
        raw = data['raw_inputs']
        cost_lakhs = round(data['estimated_cost'] / 100000, 1)
        budget_lakhs = round(raw['budget'] / 100000, 1)
        metric_data = [
            [Paragraph("<b>Detail</b>", body_style), Paragraph("<b>Value</b>", body_style)],
            [Paragraph("Total Plot Size", body_style), Paragraph(f"{raw['total_area']:.0f} sq ft  ({raw['width']:.0f} ft wide x {raw['length']:.0f} ft long)", body_style)],
            [Paragraph("Location", body_style), Paragraph(f"{raw['location']}", body_style)],
            [Paragraph("Area to Build On", body_style), Paragraph(f"{data['recommended_built_up']:.0f} sq ft", body_style)],
            [Paragraph("Open Space Left", body_style), Paragraph(f"{data['remaining_open']:.0f} sq ft", body_style)],
            [Paragraph("Construction Style", body_style), Paragraph(f"{raw['construction_type']}", body_style)],
            [Paragraph("Material Quality", body_style), Paragraph(f"{raw['material_quality']}", body_style)],
            [Paragraph("Your Budget", body_style), Paragraph(f"₹{budget_lakhs} Lakhs", body_style)],
            [Paragraph("Estimated Build Cost", body_style), Paragraph(f"₹{cost_lakhs} Lakhs  (@ ₹3,500/sqft)", body_style)],
            [Paragraph("Expected Time to Complete", body_style), Paragraph(f"{data['construction_time']} months", body_style)]
        ]
        
        t = Table(metric_data, colWidths=[2.5*inch, 4.0*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        # Fix text colors for header row inside Table
        metric_data[0] = [
            Paragraph("<b><font color='white'>Detail</font></b>", body_style),
            Paragraph("<b><font color='white'>Value</font></b>", body_style)
        ]
        t = Table(metric_data, colWidths=[2.5*inch, 4.0*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("3. Quality Scores", h1_style))
        score_data = [
            [
                Paragraph(f"<b>Safety Index:</b> {data['safety_score']}%", body_style),
                Paragraph(f"<b>Energy Efficiency:</b> {data['energy_efficiency']}%", body_style)
            ],
            [
                Paragraph(f"<b>Sustainability Rating:</b> {data['sustainability_rating']} / 5.0", body_style),
                Paragraph(f"<b>Future Expansion Capability:</b> {data['future_expansion_score']}%", body_style)
            ]
        ]
        t_score = Table(score_data, colWidths=[3.25*inch, 3.25*inch])
        t_score.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('BOX', (0,0), (-1,-1), 1, secondary_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_score)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("4. AI Tips & Suggestions", h1_style))
        for insight in data['insights']:
            story.append(Paragraph(f"• {insight}", bullet_style))
            
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(Paragraph("<i>Disclaimer: This report is generated by the Construction Intelligence Hub AI Engine. All measurements, architectural placements, and construction cost forecasts are estimations for planning purposes only.</i>", ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)))
        
        # Build Document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
