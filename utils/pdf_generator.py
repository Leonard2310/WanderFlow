"""
PDF Generator Module for TripMatch Application

This module provides functionality to generate enhanced PDF documents
for travel itineraries with professional styling and formatting.
"""

import uuid
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, NextPageTemplate, PageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFGenerator:
    """Enhanced PDF Generator for travel itineraries"""
    
    # Color palette
    COLORS = {
        'primary': HexColor('#667eea'),
        'secondary': HexColor('#764ba2'),
        'accent': HexColor('#28a745'),
        'text': HexColor('#333333'),
        'light_grey': HexColor('#f8f9fa'),
        'border': HexColor('#e9ecef')
    }
    
    def __init__(self, title: str = "Travel Itinerary", author: str = "TripMatch"):
        """
        Initialize the PDF generator
        
        Args:
            title: Document title
            author: Document author
        """
        self.title = title
        self.author = author
        self.created_date = datetime.now()
        self.styles = self._create_styles()
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=self.COLORS['primary'],
                spaceAfter=30,
                spaceBefore=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=self.COLORS['secondary'],
                spaceAfter=20,
                spaceBefore=15,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=self.COLORS['primary'],
                spaceAfter=12,
                spaceBefore=15,
                fontName='Helvetica-Bold',
                leftIndent=10
            ),
            
            'body': ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                leftIndent=15,
                rightIndent=15
            ),
            
            'highlight': ParagraphStyle(
                'CustomHighlight',
                parent=styles['Normal'],
                fontSize=12,
                leading=16,
                spaceAfter=10,
                fontName='Helvetica-Bold',
                textColor=self.COLORS['accent'],
                leftIndent=20
            ),
            
            'footer': ParagraphStyle(
                'CustomFooter',
                parent=styles['Normal'],
                fontSize=9,
                textColor=grey,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
        }
        
        return custom_styles
    
    def create_itinerary_pdf(self, 
                           itinerary_text: str, 
                           user_preferences: Optional[Dict[str, Any]] = None,
                           destination: Optional[str] = None,
                           duration: Optional[int] = None) -> BytesIO:
        """
        Create an enhanced PDF for a travel itinerary
        
        Args:
            itinerary_text: The main itinerary content
            user_preferences: User preferences data
            destination: Destination country/city
            duration: Trip duration in days
            
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        
        try:
            # Create document with custom page template
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                leftMargin=25*mm,
                rightMargin=25*mm,
                topMargin=30*mm,
                bottomMargin=30*mm,
                title=self.title,
                author=self.author
            )
            
            # Build the story (content)
            story = []
            
            # Add header
            story.extend(self._create_header(destination, duration))
            
            # Add user preferences section if provided
            if user_preferences:
                story.extend(self._create_preferences_section(user_preferences))
            
            # Add main itinerary content
            story.extend(self._create_itinerary_section(itinerary_text))
            
            # Add footer information
            story.extend(self._create_footer_section())
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_decoration, 
                     onLaterPages=self._add_page_decoration)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            raise Exception(f"Error creating PDF: {str(e)}")
    
    def _create_header(self, destination: Optional[str], duration: Optional[int]) -> List:
        """Create the PDF header section"""
        story = []
        
        # Main title
        story.append(Paragraph("🌍 Your Travel Itinerary", self.styles['title']))
        story.append(Spacer(1, 15))
        
        # Subtitle with destination and duration
        subtitle_parts = []
        if destination:
            subtitle_parts.append(f"Destination: {destination}")
        if duration:
            subtitle_parts.append(f"Duration: {duration} days")
        
        if subtitle_parts:
            subtitle = " | ".join(subtitle_parts)
            story.append(Paragraph(subtitle, self.styles['subtitle']))
        
        # Generation date
        date_str = self.created_date.strftime("%B %d, %Y")
        story.append(Paragraph(f"Generated on {date_str}", self.styles['footer']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_preferences_section(self, preferences: Dict[str, Any]) -> List:
        """Create the user preferences section"""
        story = []
        
        story.append(Paragraph("📋 Your Travel Preferences", self.styles['heading']))
        story.append(Spacer(1, 10))
        
        # Create preferences table
        pref_data = []
        
        for key, value in preferences.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            
            pref_data.append([
                Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['body']),
                Paragraph(value_str, self.styles['body'])
            ])
        
        if pref_data:
            pref_table = Table(pref_data, colWidths=[40*mm, 120*mm])
            pref_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light_grey']),
                ('GRID', (0, 0), (-1, -1), 1, self.COLORS['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(pref_table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_itinerary_section(self, itinerary_text: str) -> List:
        """Create the main itinerary content section"""
        story = []
        
        story.append(Paragraph("🗺️ Your Detailed Itinerary", self.styles['heading']))
        story.append(Spacer(1, 15))
        
        # Process the itinerary text
        paragraphs = itinerary_text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Check if it's a day header (starts with "Day" or contains "Day")
            if paragraph.strip().lower().startswith('day') or 'day' in paragraph.lower()[:10]:
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"📅 {paragraph.strip()}", self.styles['highlight']))
                story.append(Spacer(1, 5))
            else:
                # Regular paragraph
                story.append(Paragraph(paragraph.strip(), self.styles['body']))
        
        return story
    
    def _create_footer_section(self) -> List:
        """Create the footer section"""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("─" * 50, self.styles['footer']))
        story.append(Spacer(1, 15))
        
        # Travel tips
        story.append(Paragraph("✈️ Travel Tips", self.styles['heading']))
        
        tips = [
            "• Check visa requirements and passport validity before traveling",
            "• Consider travel insurance for peace of mind",
            "• Keep digital and physical copies of important documents",
            "• Research local customs and cultural etiquette",
            "• Download offline maps and translation apps",
            "• Pack according to weather and planned activities"
        ]
        
        for tip in tips:
            story.append(Paragraph(tip, self.styles['body']))
        
        story.append(Spacer(1, 20))
        
        # Powered by
        story.append(Paragraph(
            "Generated with ❤️ by <b>TripMatch</b> - Your AI Travel Planner",
            self.styles['footer']
        ))
        
        return story
    
    def _add_page_decoration(self, canvas_obj, doc):
        """Add decorative elements to each page"""
        # Add header line
        canvas_obj.setStrokeColor(self.COLORS['primary'])
        canvas_obj.setLineWidth(2)
        canvas_obj.line(30*mm, A4[1] - 20*mm, A4[0] - 30*mm, A4[1] - 20*mm)
        
        # Add footer line
        canvas_obj.line(30*mm, 20*mm, A4[0] - 30*mm, 20*mm)
        
        # Add page number
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(grey)
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawRightString(A4[0] - 30*mm, 15*mm, f"Page {page_num}")
        
        # Add watermark
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica-Bold', 40)
        canvas_obj.setFillColor(self.COLORS['light_grey'])
        canvas_obj.rotate(45)
        canvas_obj.drawCentredText(300, -200, "TripMatch")
        canvas_obj.restoreState()
    
    @staticmethod
    def create_simple_pdf(text: str, filename: Optional[str] = None) -> BytesIO:
        """
        Create a simple PDF with basic formatting
        
        Args:
            text: Text content to include
            filename: Optional filename (for metadata)
            
        Returns:
            BytesIO buffer containing the PDF
        """
        generator = PDFGenerator(title=filename or "Travel Document")
        return generator.create_itinerary_pdf(text)
    
    @staticmethod
    def create_enhanced_pdf(itinerary_text: str, 
                          user_data: Optional[Dict[str, Any]] = None) -> BytesIO:
        """
        Create an enhanced PDF with full formatting (backward compatibility)
        
        Args:
            itinerary_text: The itinerary content
            user_data: Optional user preferences and data
            
        Returns:
            BytesIO buffer containing the PDF
        """
        generator = PDFGenerator()
        
        # Extract data from user_data if provided
        preferences = user_data.get('preferences', {}) if user_data else {}
        destination = user_data.get('destination') if user_data else None
        duration = user_data.get('duration') if user_data else None
        
        return generator.create_itinerary_pdf(
            itinerary_text, 
            preferences, 
            destination, 
            duration
        )