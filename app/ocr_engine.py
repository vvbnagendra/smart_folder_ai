import os
from PIL import Image
from typing import Optional

def ocr_file(filepath: str) -> str:
    """
    Enhanced OCR function with better file handling and more realistic output.
    In a real app, this would use Tesseract, PaddleOCR, or cloud OCR services.
    """
    if not os.path.exists(filepath):
        return ""
    
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        try:
            # Verify it's a valid image
            with Image.open(filepath) as img:
                # Get image info for more realistic mock content
                width, height = img.size
                mode = img.mode
            
            # Generate more realistic OCR content based on filename
            filename = os.path.basename(filepath).lower()
            
            # Different mock content based on filename patterns
            if 'invoice' in filename or 'bill' in filename:
                return generate_invoice_text(filename)
            elif 'document' in filename or 'report' in filename:
                return generate_document_text(filename)
            elif 'receipt' in filename:
                return generate_receipt_text(filename)
            elif 'screenshot' in filename or 'screen' in filename:
                return generate_screenshot_text(filename)
            elif 'note' in filename or 'memo' in filename:
                return generate_note_text(filename)
            else:
                return generate_generic_text(filename)
                
        except Exception as e:
            print(f"Error processing image {filepath}: {e}")
            return ""
            
    elif ext == '.pdf':
        # Mock PDF OCR
        filename = os.path.basename(filepath).lower()
        if 'financial' in filename or 'report' in filename:
            return generate_financial_report_text(filename)
        elif 'manual' in filename or 'guide' in filename:
            return generate_manual_text(filename)
        else:
            return generate_pdf_text(filename)
    
    return ""

def generate_invoice_text(filename: str) -> str:
    """Generate realistic invoice OCR text."""
    return f"""INVOICE
Invoice #: INV-2024-001
Date: March 15, 2024

Bill To:
John Smith
123 Main Street
Anytown, ST 12345

Description: Professional services
Amount: $1,250.00
Tax: $125.00
Total: $1,375.00

Payment Terms: Net 30 days
Due Date: April 14, 2024

Thank you for your business!
File: {filename}"""

def generate_document_text(filename: str) -> str:
    """Generate realistic document OCR text."""
    return f"""PROJECT PROPOSAL
Document Title: Strategic Planning Initiative

Executive Summary:
This document outlines the strategic planning initiative for Q2 2024. 
The project aims to improve operational efficiency and reduce costs by 15%.

Key Objectives:
1. Process optimization
2. Technology integration
3. Staff training and development
4. Performance metrics establishment

Timeline: April - June 2024
Budget: $50,000
Expected ROI: 25% within 12 months

Document source: {filename}"""

def generate_receipt_text(filename: str) -> str:
    """Generate realistic receipt OCR text."""
    return f"""GROCERY STORE RECEIPT
Store #1234
123 Commerce St
City, ST 12345

Date: 03/15/2024 Time: 14:32

Items:
Milk 2% Gallon     $3.99
Bread Whole Wheat  $2.49
Bananas (2.5 lbs)  $1.87
Chicken Breast     $8.99
Eggs (12 count)    $2.99

Subtotal:         $20.33
Tax:              $1.63
Total:            $21.96

Payment: Credit Card
Thank you for shopping with us!

Receipt: {filename}"""

def generate_screenshot_text(filename: str) -> str:
    """Generate realistic screenshot OCR text."""
    return f"""APPLICATION INTERFACE
Dashboard - Analytics View

Current Status: Active
Users Online: 1,247
System Load: 78%
Memory Usage: 65%

Recent Activity:
- New user registration: 45 today
- File uploads: 156 today
- Search queries: 892 today

Navigation:
Home | Analytics | Settings | Users | Reports

Last Updated: March 15, 2024 2:30 PM
Screenshot: {filename}"""

def generate_note_text(filename: str) -> str:
    """Generate realistic handwritten note OCR text."""
    return f"""MEETING NOTES
Date: March 15, 2024

Attendees:
- Sarah Johnson (Project Manager)
- Mike Chen (Developer)
- Lisa Wang (Designer)

Discussion Points:
1. Review current sprint progress
2. Address user feedback on UI changes
3. Plan next iteration features
4. Discuss timeline adjustments

Action Items:
- Update wireframes by Friday
- Fix login issue (Priority: High)
- Schedule user testing session
- Prepare demo for stakeholders

Next Meeting: March 22, 2024
Notes file: {filename}"""

def generate_financial_report_text(filename: str) -> str:
    """Generate realistic financial report OCR text."""
    return f"""QUARTERLY FINANCIAL REPORT
Q1 2024 Performance Summary

Revenue:
- Total Revenue: $2,450,000
- Growth: +12% vs Q1 2023
- Recurring Revenue: $1,850,000

Expenses:
- Operating Expenses: $1,200,000
- R&D: $450,000
- Marketing: $300,000
- Administrative: $200,000

Net Income: $300,000
Profit Margin: 12.2%

Key Performance Indicators:
- Customer Acquisition Cost: $125
- Customer Lifetime Value: $2,400
- Monthly Recurring Revenue: $617,000

Report: {filename}"""

def generate_manual_text(filename: str) -> str:
    """Generate realistic manual/guide OCR text."""
    return f"""USER MANUAL
Software Installation Guide

Chapter 3: Configuration Settings

3.1 System Requirements
- Operating System: Windows 10 or later
- RAM: 8GB minimum, 16GB recommended
- Storage: 500MB available space
- Network: Internet connection required

3.2 Installation Steps
1. Download the installer from our website
2. Run the setup file as administrator
3. Follow the installation wizard
4. Enter your license key when prompted
5. Complete the setup process

3.3 Initial Configuration
After installation, configure the following:
- User preferences
- Network settings
- Data backup location
- Security settings

For technical support, contact: support@company.com
Manual: {filename}"""

def generate_pdf_text(filename: str) -> str:
    """Generate generic PDF OCR text."""
    return f"""DOCUMENT CONTENT
PDF Document Extract

This document contains important information regarding the project specifications and requirements. 

Section 1: Overview
The purpose of this document is to outline the key components and deliverables for the upcoming project phase.

Section 2: Technical Specifications
- Platform compatibility requirements
- Performance benchmarks
- Security considerations
- Integration points

Section 3: Implementation Timeline
Phase 1: Planning and Design (2 weeks)
Phase 2: Development (6 weeks)
Phase 3: Testing and QA (2 weeks)
Phase 4: Deployment (1 week)

For questions or clarifications, please refer to the appendix or contact the project team.

Source: {filename}"""

def generate_generic_text(filename: str) -> str:
    """Generate generic OCR text for unknown image types."""
    return f"""TEXT CONTENT DETECTED
Image Analysis Results

This image contains various text elements and visual components. The optical character recognition system has identified readable text content within the image.

Content may include:
- Headings and titles
- Body text paragraphs
- Lists and bullet points
- Captions and labels
- Technical specifications
- Contact information

The extracted text has been processed and indexed for search capabilities. Use the search function to locate specific terms or phrases within this content.

Image file: {filename}
Processing date: March 15, 2024
OCR confidence: 95%"""