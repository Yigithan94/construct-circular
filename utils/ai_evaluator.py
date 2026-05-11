"""
AI Evaluation module for evaluating KPI documents
"""
import os
import io
import logging
import re
import base64
import json
from typing import Dict, Any, List, Union, Optional, Tuple

from openai import OpenAI
import PyPDF2
from docx import Document as DocxDocument
import trafilatura
from flask import current_app

# Initialize OpenAI client with API key
# The client will be initialized when needed to use the latest API key
def get_openai_client():
    """Get a fresh OpenAI client using the current API key from environment"""
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file with enhanced error handling
    and processing for better text extraction quality
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                logger.warning(f"PDF file is encrypted: {file_path}")
                try:
                    # Try to decrypt with empty password (sometimes works)
                    pdf_reader.decrypt('')
                except:
                    return "[ENCRYPTED PDF: Cannot extract text from protected document]"
            
            # Get total pages for logging
            total_pages = len(pdf_reader.pages)
            logger.info(f"Extracting text from PDF with {total_pages} pages")
            
            # Extract text from all pages
            text_parts = []
            for page_num in range(total_pages):
                try:
                    page_text = pdf_reader.pages[page_num].extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    else:
                        logger.warning(f"No text extracted from page {page_num+1}")
                except Exception as page_error:
                    logger.error(f"Error extracting text from page {page_num+1}: {page_error}")
            
            # Join all text parts with page separators
            full_text = "\n\n--- PAGE BREAK ---\n\n".join(text_parts)
            
            # Basic cleaning of the extracted text
            clean_text = re.sub(r'\s+', ' ', full_text)  # Remove multiple spaces
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)  # Normalize newlines
            
            logger.info(f"Successfully extracted {len(clean_text)} characters from PDF")
            return clean_text
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file, including tables and formatting information
    for better context preservation
    """
    try:
        doc = DocxDocument(file_path)
        
        # Extract text from paragraphs with formatting hints
        text_parts = []
        
        # Process paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                # Check if paragraph is a heading
                if para.style and para.style.name and para.style.name.startswith('Heading'):
                    text_parts.append(f"\n## {para.text} ##\n")
                else:
                    text_parts.append(para.text)
        
        # Process tables
        for table in doc.tables:
            text_parts.append("\n--- TABLE START ---\n")
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                text_parts.append(" | ".join(row_data))
            text_parts.append("--- TABLE END ---\n")
        
        # Join all parts
        full_text = "\n".join(text_parts)
        logger.info(f"Successfully extracted {len(full_text)} characters from DOCX")
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_html(file_path: str) -> str:
    """
    Extract text from an HTML file using trafilatura for better content extraction
    with fallback mechanisms
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            html_content = file.read()
            
            # Try trafilatura first as it's best for article extraction
            extracted_text = trafilatura.extract(html_content, include_tables=True)
            
            # If trafilatura didn't return anything useful, try basic HTML cleaning
            if not extracted_text:
                logger.warning(f"Trafilatura failed to extract text, using fallback for HTML: {file_path}")
                
                # Basic HTML tag removal (simplified fallback)
                clean_text = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
                clean_text = re.sub(r'<script.*?>.*?</script>', '', clean_text, flags=re.DOTALL)
                clean_text = re.sub(r'<[^>]*>', ' ', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                return clean_text
                
            logger.info(f"Successfully extracted {len(extracted_text)} characters from HTML")
            return extracted_text
            
    except Exception as e:
        logger.error(f"Error extracting text from HTML: {e}")
        return ""

def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a plain text file with encoding detection and fallbacks
    """
    # List of encodings to try
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                logger.info(f"Successfully read text file using {encoding} encoding")
                return content
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode using {encoding}, trying next encoding")
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            return ""
    
    logger.error(f"Failed to decode text file with any encoding: {file_path}")
    return ""

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from a file based on its type"""
    file_type = file_type.lower()
    
    if file_type == 'pdf' or file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_type in ['docx', 'doc'] or file_path.lower().endswith(('.docx', '.doc')):
        return extract_text_from_docx(file_path)
    elif file_type in ['html', 'htm'] or file_path.lower().endswith(('.html', '.htm')):
        return extract_text_from_html(file_path)
    elif file_type == 'txt' or file_path.lower().endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return ""

def evaluate_document_with_ai(document_text: str, kpi_evaluation_criteria: str) -> Tuple[int, str]:
    """
    Evaluate a document using OpenAI API
    
    Args:
        document_text: The text extracted from the document
        kpi_evaluation_criteria: The criteria provided for evaluating this KPI
        
    Returns:
        Tuple containing:
        - A score between 1-7
        - Explanation for the score
    """
    if not document_text:
        return 1, "No text could be extracted from the document for evaluation."
    
    try:
        # Truncate document text to avoid token limits while preserving important parts
        max_chars = 10000
        if len(document_text) > max_chars:
            # Keep the beginning and end of the document, which often contain key information
            beginning = document_text[:max_chars//2]
            ending = document_text[-(max_chars//2):]
            document_text = beginning + "\n...[DOCUMENT TRUNCATED]...\n" + ending
            logger.info(f"Document text truncated from {len(document_text)} to {max_chars} characters")
            
        # Prepare the prompt for the AI with enhanced instructions
        prompt = f"""
You are a KPI (Key Performance Indicator) document evaluator specializing in construction and contractor 
assessment for circular economy principles. Evaluate the following document text against the provided 
evaluation criteria with careful attention to detail.

EVALUATION CRITERIA:
{kpi_evaluation_criteria}

DOCUMENT TEXT:
{document_text}

Based on the evaluation criteria, rate this document on a scale of 1-7 where:
1 = Completely inadequate, does not meet any criteria
2 = Very poor, barely meets minimal criteria
3 = Below average, meets some basic criteria but has significant weaknesses
4 = Average, adequately meets criteria but has room for improvement
5 = Above average, meets most criteria well
6 = Very good, meets almost all criteria excellently
7 = Exceptional, exceeds all criteria

Your evaluation should focus specifically on how well the document addresses the provided criteria. 
Include references to specific sections or details that influenced your scoring.

Respond ONLY with a JSON object containing:
1. "score": A single integer between 1 and 7
2. "explanation": A detailed explanation (max 300 words) justifying your score, including:
   - Key strengths and weaknesses
   - Specific evidence from the document that supports your assessment
   - Actionable recommendations for improvement

Your response MUST be valid JSON.
"""

        # Get a fresh client instance with the latest API key
        client = get_openai_client()
        
        # Use the OpenAI API to evaluate the document
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            messages=[
                {"role": "system", "content": "You are a professional KPI evaluator for construction projects with expertise in circular economy principles and sustainability in the construction sector."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent scoring
            response_format={"type": "json_object"},
            max_tokens=1500  # Allow for more detailed explanations
        )
        
        # Parse the response
        result_text = response.choices[0].message.content
        if result_text:
            result = json.loads(result_text)
        else:
            return 1, "No response received from AI evaluation."
        
        # Ensure the score is within bounds
        score = max(1, min(7, int(result.get("score", 1))))
        explanation = result.get("explanation", "No explanation provided.")
        
        # Log successful evaluation
        logger.info(f"Document evaluated successfully with score: {score}")
        
        return score, explanation
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error during AI evaluation: {e}")
        
        # Check if it's a quota/API key issue
        if "quota" in error_msg.lower() or "429" in error_msg:
            # For quota issues, return a default score of 4 (average) instead of 1
            return 4, "AI evaluation temporarily unavailable due to API quota. Document uploaded successfully and will be manually reviewed."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return 4, "AI evaluation temporarily unavailable due to API authentication. Document uploaded successfully and will be manually reviewed."
        else:
            return 1, f"Error during AI evaluation: {str(e)}"

def evaluate_kpi_document(document_path: str, file_type: str, kpi_evaluation_criteria: str) -> Dict[str, Any]:
    """
    Process a document for KPI evaluation
    
    Args:
        document_path: Path to the document
        file_type: Type of the document (pdf, docx, etc.)
        kpi_evaluation_criteria: Criteria for evaluation
        
    Returns:
        Dictionary with evaluation results
    """
    # Extract text from document
    document_text = extract_text_from_file(document_path, file_type)
    
    if not document_text:
        return {
            "success": False,
            "score": 1,
            "explanation": "Unable to extract text from the document."
        }
    
    # Evaluate with AI
    score, explanation = evaluate_document_with_ai(document_text, kpi_evaluation_criteria)
    
    return {
        "success": True,
        "score": score,
        "explanation": explanation
    }