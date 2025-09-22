import PyPDF2
import docx
import os
import re
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text into sentences"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_key_information(self, text: str) -> Dict[str, Any]:
        """Extract key information patterns from text"""
        patterns = {
            'times': r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?|\d{1,2}\s*(?:AM|PM|am|pm))\b',
            'dates': r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})\b',
            'percentages': r'\b(\d+(?:\.\d+)?%)\b',
            'numbers': r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b',
            'durations': r'\b(\d+\s*(?:day|week|month|year|hour|minute)s?)\b',
            'requirements': r'(?:must|shall|required|mandatory|minimum|maximum)[\s\w]*',
            'policies': r'(?:policy|rule|regulation|guideline|procedure)[\s\w]*'
        }
        
        extracted = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted[pattern_name] = matches
        
        return extracted
