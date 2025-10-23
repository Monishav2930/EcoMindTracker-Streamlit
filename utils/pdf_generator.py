"""
PDF Report Generator for EcoMind
Creates comprehensive PDF reports with charts and statistics
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, date
import io
from typing import List, Dict

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00C851'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#FFD700'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Section header style
        self.header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#00C851'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Normal style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_user_report(
        self,
        username: str,
        user_level: str,
        total_score: int,
        stats: Dict,
        badges: List[str],
        activity_logs: List[Dict],
        start_date: date = None,
        end_date: date = None
    ) -> bytes:
        """
        Generate a comprehensive PDF report for a user
        
        Args:
            username: User's username
            user_level: Current level (Bronze, Silver, etc.)
            total_score: Total points earned
            stats: Statistics dictionary
            badges: List of badge names
            activity_logs: List of activity log dictionaries
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
        
        Returns:
            bytes: PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Title
        title = Paragraph("EcoMind Carbon Footprint Report", self.title_style)
        story.append(title)
        
        # Subtitle with date
        report_date = datetime.now().strftime('%B %d, %Y')
        subtitle = Paragraph(f'"Track Smarter. Go Greener." - Generated on {report_date}', self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.3*inch))
        
        # User Information Section
        story.append(Paragraph("User Profile", self.header_style))
        
        user_data = [
            ['Username:', username],
            ['Current Level:', user_level],
            ['Total Score:', f'{total_score} points'],
            ['Days Tracked:', str(stats.get('total_days', 0))],
        ]
        
        user_table = Table(user_data, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Statistics Section
        story.append(Paragraph("Carbon Footprint Statistics", self.header_style))
        
        if start_date and end_date:
            period_text = Paragraph(
                f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                self.normal_style
            )
            story.append(period_text)
            story.append(Spacer(1, 0.1*inch))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total CO₂ Emissions', f"{stats.get('total_co2', 0):.2f}g"],
            ['Daily Average', f"{stats.get('avg_daily_co2', 0):.2f}g"],
            ['Best Day (Lowest)', f"{stats.get('best_day_co2', 0):.2f}g"],
            ['Worst Day (Highest)', f"{stats.get('worst_day_co2', 0):.2f}g"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00C851')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F8E9')]),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Global Comparison
        global_avg = 2500
        user_avg = stats.get('avg_daily_co2', 0)
        if user_avg > 0:
            comparison = ((global_avg - user_avg) / global_avg * 100)
            comparison_text = f"You are {abs(comparison):.1f}% {'below' if comparison > 0 else 'above'} the global average of 2500g/day"
            story.append(Paragraph(f"<b>Global Comparison:</b> {comparison_text}", self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Badges Section
        if badges:
            story.append(Paragraph("Achievements & Badges", self.header_style))
            badges_text = ", ".join(badges)
            story.append(Paragraph(f"<b>Earned Badges ({len(badges)}):</b> {badges_text}", self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Activity Breakdown
        if activity_logs:
            story.append(Paragraph("Activity Summary", self.header_style))
            
            # Calculate totals
            total_emails = sum(log.get('emails', 0) for log in activity_logs)
            total_video = sum(log.get('video_calls', 0) for log in activity_logs)
            total_streaming = sum(log.get('streaming', 0) for log in activity_logs)
            avg_cloud = sum(log.get('cloud_storage', 0) for log in activity_logs) / len(activity_logs)
            total_device = sum(log.get('device_usage', 0) for log in activity_logs)
            
            activity_data = [
                ['Activity Type', 'Total/Average', 'CO₂ Impact'],
                ['Emails Sent', f'{int(total_emails)} emails', f'{total_emails * 4:.2f}g'],
                ['Video Calls', f'{total_video:.1f} hours', f'{total_video * 150:.2f}g'],
                ['Streaming', f'{total_streaming:.1f} hours', f'{total_streaming * 36:.2f}g'],
                ['Cloud Storage', f'{avg_cloud:.1f}GB avg', f'{avg_cloud * 10:.2f}g/day'],
                ['Device Usage', f'{total_device:.1f} hours', f'{total_device * 20:.2f}g'],
            ]
            
            activity_table = Table(activity_data, colWidths=[2*inch, 2*inch, 2*inch])
            activity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00C851')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F8E9')]),
            ]))
            story.append(activity_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations Section
        story.append(Paragraph("Eco-Friendly Recommendations", self.header_style))
        
        recommendations = [
            "• Batch emails instead of sending individually to reduce server load",
            "• Use audio-only for meetings when video isn't necessary (saves 96% bandwidth)",
            "• Lower streaming quality from HD to SD when possible",
            "• Perform regular cloud storage cleanup to remove unused files",
            "• Enable power saving mode on devices",
            "• Close idle browser tabs to reduce memory and CPU usage",
            "• Use dark mode on OLED screens to save energy",
            "• Schedule regular digital detox breaks"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.normal_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer_text = Paragraph(
            f"<i>This report was generated by EcoMind on {report_date}. "
            "For more information, visit your EcoMind dashboard.</i>",
            footer_style
        )
        story.append(Spacer(1, 0.3*inch))
        story.append(footer_text)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_analytics_report(
        self,
        username: str,
        activity_logs: List[Dict],
        start_date: date,
        end_date: date
    ) -> bytes:
        """
        Generate an analytics-focused PDF report
        
        Args:
            username: User's username
            activity_logs: List of activity log dictionaries
            start_date: Start date for the report
            end_date: End date for the report
        
        Returns:
            bytes: PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Title
        title = Paragraph("EcoMind Analytics Report", self.title_style)
        story.append(title)
        
        # Period subtitle
        period = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        subtitle = Paragraph(f"Analysis Period: {period}", self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.2*inch))
        
        # User info
        story.append(Paragraph(f"<b>User:</b> {username}", self.normal_style))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics
        if activity_logs:
            story.append(Paragraph("Summary Statistics", self.header_style))
            
            total_days = len(activity_logs)
            total_co2 = sum(log.get('co2_grams', 0) for log in activity_logs)
            avg_co2 = total_co2 / total_days if total_days > 0 else 0
            min_co2 = min(log.get('co2_grams', 0) for log in activity_logs)
            max_co2 = max(log.get('co2_grams', 0) for log in activity_logs)
            
            summary_data = [
                ['Metric', 'Value'],
                ['Days Analyzed', str(total_days)],
                ['Total CO₂ Emissions', f'{total_co2:.2f}g'],
                ['Daily Average', f'{avg_co2:.2f}g'],
                ['Best Day (Lowest)', f'{min_co2:.2f}g'],
                ['Worst Day (Highest)', f'{max_co2:.2f}g'],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00C851')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F8E9')]),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Detailed activity logs table (limited to last 20 entries)
            story.append(Paragraph("Detailed Activity Log (Last 20 Entries)", self.header_style))
            
            log_data = [['Date', 'Emails', 'Video (hrs)', 'Streaming (hrs)', 'Cloud (GB)', 'Device (hrs)', 'CO₂ (g)']]
            
            for log in activity_logs[-20:]:  # Last 20 entries
                log_data.append([
                    log.get('date', ''),
                    str(int(log.get('emails', 0))),
                    f"{log.get('video_calls', 0):.1f}",
                    f"{log.get('streaming', 0):.1f}",
                    f"{log.get('cloud_storage', 0):.1f}",
                    f"{log.get('device_usage', 0):.1f}",
                    f"{log.get('co2_grams', 0):.1f}"
                ])
            
            log_table = Table(log_data, colWidths=[1.1*inch, 0.6*inch, 0.8*inch, 0.9*inch, 0.7*inch, 0.8*inch, 0.7*inch])
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00C851')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F8E9')]),
            ]))
            story.append(log_table)
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
