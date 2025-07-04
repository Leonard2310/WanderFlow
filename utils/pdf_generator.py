"""
PDF Generator Module for WanderFlow Application

This module provides functionality to generate enhanced PDF documents
for travel itineraries with professional styling and formatting.
"""

import re
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas


class PDFGenerator:
    """
    Enhanced PDF generator for travel itineraries with professional styling.
    
    This class provides comprehensive PDF generation capabilities for travel
    itineraries, including custom styling, branding, and multiple content
    sections. Features WanderFlow branding and professional layout design.
    """
    
    # Color palette - WanderFlow brand colors
    COLORS = {
        'primary': HexColor('#667eea'),        # WanderFlow primary blue
        'secondary': HexColor('#764ba2'),      # WanderFlow secondary purple
        'accent': HexColor('#28a745'),         # Success green
        'text': HexColor('#2c3e50'),          # Dark text
        'light_blue': HexColor('#A1C4FD'),     # Light blue from gradient
        'light_purple': HexColor('#C2E9FB'),   # Light purple from gradient
        'light_grey': HexColor('#f8f9fa'),     # Light background
        'border': HexColor('#e9ecef'),         # Border color
        'white': HexColor('#ffffff')           # White
    }
    
    def __init__(self, title: str = "WanderFlow Travel Itinerary", author: str = "WanderFlow AI Travel Planner"):
        """
        Initialize the PDF generator with WanderFlow branding.
        
        Sets up the PDF generator with default styling, colors, and metadata
        for creating professional travel itinerary documents.
        
        Args:
            title (str): Document title for metadata and headers
            author (str): Document author for metadata
        """
        self.title = title
        self.author = author
        self.created_date = datetime.now()
        self.styles = self._create_styles()
    
    def _remove_markdown_formatting(self, text: str) -> str:
        """
        Remove markdown formatting from text while preserving structure.
        
        Cleans up markdown syntax including bold, italic, headers, links,
        and code blocks while maintaining readability and line breaks.
        
        Args:
            text (str): Text content with markdown formatting
            
        Returns:
            str: Clean text without markdown syntax
        """
        if not text:
            return text
            
        # Remove bold (**text** and __text__)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        
        # Remove italic (*text* and _text_)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'(?<!\w)_([^_\s].*?[^_\s])_(?!\w)', r'\1', text)
        
        # Remove code (`text`)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove strikethrough (~~text~~)
        text = re.sub(r'~~(.*?)~~', r'\1', text)
        
        # Remove headers (# ## ### etc.)
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Remove links but keep text [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Clean up extra whitespace but preserve line breaks
        # Replace multiple spaces/tabs with single space, but keep newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs -> single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple empty lines -> double newline
        text = text.strip()
        
        return text

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Create custom paragraph styles for PDF formatting.
        
        Defines a comprehensive set of paragraph styles including titles,
        headers, body text, and special formatting for different content
        sections with WanderFlow branding colors.
        
        Returns:
            Dict[str, ParagraphStyle]: Dictionary of named paragraph styles
        """
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=self.COLORS['primary'],
                spaceAfter=20,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'brand_title': ParagraphStyle(
                'BrandTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.COLORS['secondary'],
                spaceAfter=15,
                spaceBefore=5,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.COLORS['text'],
                spaceAfter=15,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            
            'section_header': ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.COLORS['primary'],
                spaceAfter=15,
                spaceBefore=20,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderColor=self.COLORS['primary'],
                borderPadding=8
            ),
            
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=self.COLORS['secondary'],
                spaceAfter=12,
                spaceBefore=15,
                fontName='Helvetica-Bold',
                leftIndent=10
            ),
            
            'body': ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                textColor=self.COLORS['text'],
                leftIndent=15,
                rightIndent=15
            ),
            
            'highlight': ParagraphStyle(
                'CustomHighlight',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=10,
                fontName='Helvetica-Bold',
                textColor=self.COLORS['accent'],
                leftIndent=20,
                backColor=self.COLORS['light_grey'],
                borderWidth=1,
                borderColor=self.COLORS['accent'],
                borderPadding=6
            ),
            
            'footer': ParagraphStyle(
                'CustomFooter',
                parent=styles['Normal'],
                fontSize=9,
                textColor=grey,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            ),
            
            'brand_footer': ParagraphStyle(
                'BrandFooter',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.COLORS['primary'],
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
        }
        
        return custom_styles
    
    def create_itinerary_pdf(self, 
                           itinerary_text: str, 
                           user_preferences: Optional[Dict[str, Any]] = None,
                           destination: Optional[str] = None,
                           duration: Optional[int] = None,
                           extra_info: Optional[str] = None) -> BytesIO:
        """
        Create an enhanced PDF document for a travel itinerary.
        
        Generates a comprehensive PDF with multiple sections including
        header, preferences, itinerary content, additional information,
        and footer with professional styling and WanderFlow branding.
        
        Args:
            itinerary_text (str): The main itinerary content
            user_preferences (Optional[Dict[str, Any]]): User travel preferences
            destination (Optional[str]): Destination country or city
            duration (Optional[int]): Trip duration in days
            extra_info (Optional[str]): Additional travel information
            
        Returns:
            BytesIO: Buffer containing the generated PDF document
            
        Raises:
            Exception: If PDF generation fails
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
            itinerary_text = self._remove_markdown_formatting(itinerary_text)
            story.extend(self._create_itinerary_section(itinerary_text))
            
            # Add additional information section if provided
            if extra_info:
                extra_info = self._remove_markdown_formatting(extra_info)
                story.extend(self._create_additional_info_section(extra_info))
            
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
        """
        Create the enhanced PDF header section with WanderFlow branding.
        
        Generates the document header including brand logo, title,
        trip details, and generation timestamp with professional formatting.
        
        Args:
            destination (Optional[str]): Travel destination name
            duration (Optional[int]): Trip duration in days
            
        Returns:
            List: List of ReportLab flowable elements for the header
        """
        story = []
        
        # WanderFlow brand header
        story.append(Paragraph("WanderFlow", self.styles['brand_title']))
        story.append(Paragraph("Your AI-Powered Travel Planner", self.styles['footer']))
        story.append(Spacer(1, 20))
        
        # Decorative line
        story.append(Paragraph("─" * 60, self.styles['footer']))
        story.append(Spacer(1, 15))
        
        # Main title
        story.append(Paragraph("Your Personalized Travel Itinerary", self.styles['title']))
        story.append(Spacer(1, 10))
        
        # Trip details in a nice format
        if destination or duration:
            details = []
            if destination:
                details.append(f"<b>Destination:</b> {destination}")
            if duration:
                details.append(f"<b>Duration:</b> {duration} day{'s' if duration != 1 else ''}")
            
            if details:
                for detail in details:
                    story.append(Paragraph(detail, self.styles['subtitle']))
                    story.append(Spacer(1, 5))
        
        # Generation info
        date_str = self.created_date.strftime("%B %d, %Y at %H:%M")
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Generated on {date_str}", self.styles['footer']))
        story.append(Spacer(1, 25))
        
        return story
    
    def _create_preferences_section(self, preferences: Dict[str, Any]) -> List:
        """
        Create the enhanced user preferences section.
        
        Formats user travel preferences into a professional table layout
        with proper styling and organization for easy reading.
        
        Args:
            preferences (Dict[str, Any]): User travel preferences data
            
        Returns:
            List: List of ReportLab flowable elements for preferences section
        """
        story = []
        
        story.append(Paragraph("Your Travel Preferences", self.styles['section_header']))
        story.append(Spacer(1, 10))
        
        # Create preferences in a more visual format
        pref_data = []
        
        # Add header row
        pref_data.append([
            Paragraph("<b>Preference</b>", self.styles['heading']),
            Paragraph("<b>Your Choice</b>", self.styles['heading'])
        ])
        
        for key, value in preferences.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            
            pref_data.append([
                Paragraph(f"<b>{key.replace('_', ' ').title()}</b>", self.styles['body']),
                Paragraph(value_str, self.styles['body'])
            ])
        
        if len(pref_data) > 1:  # More than just header
            pref_table = Table(pref_data, colWidths=[45*mm, 115*mm])
            pref_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light_grey']),
                ('GRID', (0, 0), (-1, -1), 1, self.COLORS['border']),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.COLORS['light_grey'], self.COLORS['white']]),
            ]))
            
            story.append(pref_table)
            story.append(Spacer(1, 25))
        
        return story
    
    def _create_itinerary_section(self, itinerary_text: str) -> List:
        """
        Create the enhanced main itinerary content section.
        
        Formats the travel itinerary with intelligent parsing for days,
        times, and activities with appropriate styling and spacing.
        
        Args:
            itinerary_text (str): Clean itinerary text content
            
        Returns:
            List: List of ReportLab flowable elements for itinerary section
        """
        story = []
        
        story.append(Paragraph("Your Detailed Travel Plan", self.styles['section_header']))
        story.append(Spacer(1, 15))
        
        # Process the itinerary text and remove markdown formatting
        clean_itinerary = self._remove_markdown_formatting(itinerary_text)
        paragraphs = clean_itinerary.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Check if it's a day header (starts with "Day" or contains "Day")
            if paragraph.strip().lower().startswith('day') or 'day' in paragraph.lower()[:15]:
                # Add extra space before each day for better readability
                story.append(Spacer(1, 25))
                # Enhanced day header with background (no emoji)
                day_text = paragraph.strip()
                story.append(Paragraph(f"{day_text}", self.styles['highlight']))
                story.append(Spacer(1, 12))
            elif any(keyword in paragraph.lower() for keyword in ['morning', 'afternoon', 'evening', 'night']):
                # Time of day headers (no emoji)
                story.append(Spacer(1, 8))
                story.append(Paragraph(f"{paragraph.strip()}", self.styles['heading']))
                story.append(Spacer(1, 5))
            else:
                # Regular paragraph with better formatting
                formatted_text = paragraph.strip()
                # Add bullet points for lists
                if formatted_text.startswith('-') or formatted_text.startswith('•'):
                    formatted_text = f"  • {formatted_text[1:].strip()}"
                story.append(Paragraph(formatted_text, self.styles['body']))
        
        return story
    
    def _create_additional_info_section(self, extra_info: str) -> List:
        """
        Create the enhanced additional information section.
        
        Formats supplementary travel information with intelligent parsing
        for different information categories and appropriate styling.
        
        Args:
            extra_info (str): Additional travel information text
            
        Returns:
            List: List of ReportLab flowable elements for additional info section
        """
        story = []
        
        story.append(Spacer(1, 25))
        story.append(Paragraph("Additional Travel Information", self.styles['section_header']))
        story.append(Spacer(1, 15))
        
        # Process the additional information text and remove markdown formatting
        clean_extra_info = self._remove_markdown_formatting(extra_info)
        paragraphs = clean_extra_info.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Check if it's a section header
            if any(keyword in paragraph.lower() for keyword in ['documents', 'vaccination', 'weather', 'dining', 'attractions', 'booking', 'transportation', 'accommodation']):
                story.append(Spacer(1, 12))
                # No emoji, just header styling
                story.append(Paragraph(f"{paragraph.strip()}", self.styles['highlight']))
                story.append(Spacer(1, 8))
            else:
                # Regular paragraph
                formatted_text = paragraph.strip()
                if formatted_text.startswith('-') or formatted_text.startswith('•'):
                    formatted_text = f"  • {formatted_text[1:].strip()}"
                story.append(Paragraph(formatted_text, self.styles['body']))
        
        return story
    
    def _create_footer_section(self) -> List:
        """
        Create the enhanced footer section with WanderFlow branding.
        
        Generates the document footer including travel tips, branding
        information, and document metadata with professional styling.
        
        Returns:
            List: List of ReportLab flowable elements for footer section
        """
        story = []
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("─" * 60, self.styles['footer']))
        story.append(Spacer(1, 20))
        
        # Enhanced travel tips section
        story.append(Paragraph("Essential Travel Tips", self.styles['section_header']))
        story.append(Spacer(1, 10))
        
        tips = [
            "Check visa requirements and passport validity (6+ months) before traveling",
            "Consider comprehensive travel insurance for peace of mind",
            "Keep digital and physical copies of important documents in separate locations",
            "Research local customs, cultural etiquette, and basic phrases",
            "Download offline maps, translation apps, and emergency contact info",
            "Pack according to weather forecasts and planned activities",
            "Notify your bank of travel plans and research local payment methods",
            "Check if any vaccinations are required for your destination"
        ]
        
        for tip in tips:
            story.append(Paragraph(tip, self.styles['body']))
            story.append(Spacer(1, 3))
        
        story.append(Spacer(1, 25))
        
        # Enhanced WanderFlow branding footer
        story.append(Paragraph("─" * 60, self.styles['footer']))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph(
            "<b>WanderFlow</b> - Your AI-Powered Travel Companion",
            self.styles['brand_footer']
        ))
        story.append(Spacer(1, 5))
        story.append(Paragraph(
            "Making every journey unforgettable with personalized AI recommendations",
            self.styles['footer']
        ))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"Generated on {self.created_date.strftime('%B %d, %Y')} | Safe travels!",
            self.styles['footer']
        ))
        
        return story
    
    def _add_page_decoration(self, canvas_obj, doc):
        """
        Add enhanced decorative elements to each page with WanderFlow branding.
        
        Applies consistent page decorations including headers, footers,
        page numbers, watermarks, and corner decorations across all pages.
        
        Args:
            canvas_obj: ReportLab canvas object for drawing
            doc: Document object containing page information
        """
        # Enhanced header with gradient-like effect
        canvas_obj.setStrokeColor(self.COLORS['primary'])
        canvas_obj.setLineWidth(3)
        canvas_obj.line(30*mm, A4[1] - 15*mm, A4[0] - 30*mm, A4[1] - 15*mm)
        
        # Secondary line
        canvas_obj.setStrokeColor(self.COLORS['secondary'])
        canvas_obj.setLineWidth(1)
        canvas_obj.line(30*mm, A4[1] - 17*mm, A4[0] - 30*mm, A4[1] - 17*mm)
        
        # Enhanced footer with multiple lines
        canvas_obj.setStrokeColor(self.COLORS['secondary'])
        canvas_obj.setLineWidth(1)
        canvas_obj.line(30*mm, 22*mm, A4[0] - 30*mm, 22*mm)
        
        canvas_obj.setStrokeColor(self.COLORS['primary'])
        canvas_obj.setLineWidth(3)
        canvas_obj.line(30*mm, 20*mm, A4[0] - 30*mm, 20*mm)
        
        # Page number with better styling
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(self.COLORS['primary'])
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawRightString(A4[0] - 30*mm, 12*mm, f"Page {page_num}")
        
        # WanderFlow branding in footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.COLORS['secondary'])
        canvas_obj.drawString(30*mm, 12*mm, "WanderFlow - AI Travel Planner")
        
        # Enhanced watermark with better positioning
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica-Bold', 35)
        canvas_obj.setFillColor(HexColor('#f0f0f0'))  # Very light gray
        canvas_obj.rotate(45)
        # Position watermark in center
        canvas_obj.drawCentredString(300, -150, "WanderFlow")
        canvas_obj.restoreState()
        
        # Small decorative elements in corners
        canvas_obj.setFillColor(self.COLORS['light_blue'])
        # Top left corner decoration
        canvas_obj.circle(35*mm, A4[1] - 25*mm, 2*mm, fill=1)
        # Bottom right corner decoration  
        canvas_obj.setFillColor(self.COLORS['secondary'])
        canvas_obj.circle(A4[0] - 35*mm, 30*mm, 2*mm, fill=1)
    
    @staticmethod
    def create_simple_pdf(text: str, filename: Optional[str] = None) -> BytesIO:
        """
        Create a simple PDF document with basic WanderFlow styling.
        
        Generates a streamlined PDF with minimal formatting but consistent
        branding for quick document creation needs.
        
        Args:
            text (str): Text content to include in the PDF
            filename (Optional[str]): Optional filename for document metadata
            
        Returns:
            BytesIO: Buffer containing the generated simple PDF
        """
        generator = PDFGenerator(title=filename or "WanderFlow Travel Document")
        return generator.create_itinerary_pdf(text)
    
    @staticmethod
    def create_enhanced_pdf(itinerary_text: str, 
                          user_data: Optional[Dict[str, Any]] = None,
                          extra_info: Optional[str] = None) -> BytesIO:
        """
        Create an enhanced PDF with comprehensive WanderFlow branding and formatting.
        
        Generates a full-featured PDF document with all sections including
        preferences, detailed itinerary, additional information, and
        professional styling throughout.
        
        Args:
            itinerary_text (str): The main travel itinerary content
            user_data (Optional[Dict[str, Any]]): User preferences and trip data
            extra_info (Optional[str]): Additional travel information and tips
            
        Returns:
            BytesIO: Buffer containing the enhanced WanderFlow PDF document
        """
        generator = PDFGenerator()
        
        # Extract relevant data from user_data if provided
        preferences = user_data.get('preferences', {}) if user_data else {}
        destination = user_data.get('destination') if user_data else None
        duration = user_data.get('duration') if user_data else None
        
        return generator.create_itinerary_pdf(
            itinerary_text, 
            preferences, 
            destination, 
            duration,
            extra_info
        )