import nltk
import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
import re
from datetime import datetime

# Download required NLTK data
try:
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class ContradictionDetector:
    def __init__(self):
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spacy english model: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Load sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load contradiction detection model
        self.contradiction_classifier = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium",
            return_all_scores=True
        )
    
    def detect_contradictions(self, documents: Dict[str, str]) -> List[Dict]:
        """Main function to detect contradictions between documents"""
        contradictions = []
        
        # Extract sentences from all documents
        doc_sentences = {}
        for doc_name, text in documents.items():
            sentences = self._extract_sentences(text)
            doc_sentences[doc_name] = sentences
        
        # Compare sentences across documents
        doc_names = list(doc_sentences.keys())
        
        for i in range(len(doc_names)):
            for j in range(i + 1, len(doc_names)):
                doc1, doc2 = doc_names[i], doc_names[j]
                doc_contradictions = self._compare_documents(
                    doc1, doc_sentences[doc1],
                    doc2, doc_sentences[doc2]
                )
                contradictions.extend(doc_contradictions)
        
        # Sort by severity score
        contradictions.sort(key=lambda x: x['severity_score'], reverse=True)
        
        return contradictions
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract meaningful sentences from text"""
        if not self.nlp:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
        else:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
        
        # Filter sentences
        filtered_sentences = []
        for sentence in sentences:
            if len(sentence) > 20 and not sentence.isdigit():
                filtered_sentences.append(sentence.strip())
        
        return filtered_sentences
    
    def _compare_documents(self, doc1_name: str, doc1_sentences: List[str], 
                          doc2_name: str, doc2_sentences: List[str]) -> List[Dict]:
        """Compare sentences between two documents"""
        contradictions = []
        
        # Check for numerical contradictions
        numerical_contradictions = self._detect_numerical_contradictions(
            doc1_name, doc1_sentences, doc2_name, doc2_sentences
        )
        contradictions.extend(numerical_contradictions)
        
        # Check for semantic contradictions
        semantic_contradictions = self._detect_semantic_contradictions(
            doc1_name, doc1_sentences, doc2_name, doc2_sentences
        )
        contradictions.extend(semantic_contradictions)
        
        # Check for policy contradictions
        policy_contradictions = self._detect_policy_contradictions(
            doc1_name, doc1_sentences, doc2_name, doc2_sentences
        )
        contradictions.extend(policy_contradictions)
        
        return contradictions
    
    def _detect_numerical_contradictions(self, doc1_name: str, doc1_sentences: List[str],
                                       doc2_name: str, doc2_sentences: List[str]) -> List[Dict]:
        """Detect numerical contradictions (times, percentages, durations)"""
        contradictions = []
        
        # Patterns for different types of numerical data
        patterns = {
            'time': r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?|\d{1,2}\s*(?:AM|PM|am|pm))\b',
            'percentage': r'\b(\d+(?:\.\d+)?%)\b',
            'duration_weeks': r'\b(\d+)\s*weeks?\b',
            'duration_days': r'\b(\d+)\s*days?\b',
            'attendance': r'attendance[:\s]*(\d+(?:\.\d+)?%)',
        }
        
        for pattern_name, pattern in patterns.items():
            doc1_matches = self._extract_numerical_contexts(doc1_sentences, pattern, pattern_name)
            doc2_matches = self._extract_numerical_contexts(doc2_sentences, pattern, pattern_name)
            
            # Compare matches
            for context1, value1, sentence1 in doc1_matches:
                for context2, value2, sentence2 in doc2_matches:
                    similarity = self._calculate_context_similarity(context1, context2)
                    
                    if similarity > 0.7 and value1 != value2:  # Same context, different values
                        contradictions.append({
                            'type': 'numerical',
                            'subtype': pattern_name,
                            'document1': doc1_name,
                            'document2': doc2_name,
                            'sentence1': sentence1,
                            'sentence2': sentence2,
                            'value1': value1,
                            'value2': value2,
                            'context_similarity': similarity,
                            'severity_score': 0.9,
                            'description': f"Conflicting {pattern_name} values: {value1} vs {value2}",
                            'suggestion': f"Clarify which {pattern_name} value is correct: {value1} or {value2}"
                        })
        
        return contradictions
    
    def _extract_numerical_contexts(self, sentences: List[str], pattern: str, pattern_type: str) -> List[Tuple]:
        """Extract numerical values with their contexts"""
        matches = []
        for sentence in sentences:
            found_values = re.findall(pattern, sentence, re.IGNORECASE)
            if found_values:
                # Extract context around the number
                context = self._extract_context(sentence, pattern_type)
                for value in found_values:
                    matches.append((context, value, sentence))
        return matches
    
    def _extract_context(self, sentence: str, pattern_type: str) -> str:
        """Extract context keywords around numerical values"""
        context_keywords = {
            'time': ['submit', 'deadline', 'due', 'close', 'open', 'start', 'end'],
            'percentage': ['attendance', 'minimum', 'required', 'pass', 'fail'],
            'duration_weeks': ['notice', 'leave', 'vacation', 'break'],
            'duration_days': ['notice', 'leave', 'vacation', 'break'],
            'attendance': ['required', 'minimum', 'mandatory']
        }
        
        keywords = context_keywords.get(pattern_type, [])
        found_keywords = []
        
        sentence_lower = sentence.lower()
        for keyword in keywords:
            if keyword in sentence_lower:
                found_keywords.append(keyword)
        
        return ' '.join(found_keywords) if found_keywords else sentence[:50]
    
    def _calculate_context_similarity(self, context1: str, context2: str) -> float:
        """Calculate similarity between two contexts"""
        if not context1 or not context2:
            return 0.0
        
        try:
            embeddings = self.sentence_model.encode([context1, context2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except:
            # Fallback to simple word overlap
            words1 = set(context1.lower().split())
            words2 = set(context2.lower().split())
            if not words1 or not words2:
                return 0.0
            overlap = len(words1.intersection(words2))
            return overlap / max(len(words1), len(words2))
    
    def _detect_semantic_contradictions(self, doc1_name: str, doc1_sentences: List[str],
                                     doc2_name: str, doc2_sentences: List[str]) -> List[Dict]:
        """Detect semantic contradictions using NLP"""
        contradictions = []
        
        # Look for opposite statements
        contradiction_patterns = [
            (r'\bmust\b', r'\bmust not\b|\bforbidden\b|\bprohibited\b'),
            (r'\brequired\b', r'\boptional\b|\bnot required\b'),
            (r'\bmandatory\b', r'\bvoluntary\b|\boptional\b'),
            (r'\ballowed\b', r'\bnot allowed\b|\bforbidden\b')
        ]
        
        for positive_pattern, negative_pattern in contradiction_patterns:
            positive_sentences = [s for s in doc1_sentences + doc2_sentences 
                                if re.search(positive_pattern, s, re.IGNORECASE)]
            negative_sentences = [s for s in doc1_sentences + doc2_sentences 
                                if re.search(negative_pattern, s, re.IGNORECASE)]
            
            for pos_sent in positive_sentences:
                for neg_sent in negative_sentences:
                    # Check if they refer to similar topics
                    similarity = self._calculate_context_similarity(pos_sent, neg_sent)
                    if similarity > 0.6:
                        doc1_has_pos = pos_sent in doc1_sentences
                        doc1_has_neg = neg_sent in doc1_sentences
                        
                        if (doc1_has_pos and not doc1_has_neg) or (not doc1_has_pos and doc1_has_neg):
                            contradictions.append({
                                'type': 'semantic',
                                'subtype': 'opposite_statements',
                                'document1': doc1_name if doc1_has_pos else doc2_name,
                                'document2': doc2_name if doc1_has_pos else doc1_name,
                                'sentence1': pos_sent,
                                'sentence2': neg_sent,
                                'similarity': similarity,
                                'severity_score': 0.8,
                                'description': 'Documents contain opposite statements about the same topic',
                                'suggestion': 'Review and align the conflicting statements'
                            })
        
        return contradictions
    
    def _detect_policy_contradictions(self, doc1_name: str, doc1_sentences: List[str],
                                    doc2_name: str, doc2_sentences: List[str]) -> List[Dict]:
        """Detect policy-level contradictions"""
        contradictions = []
        
        # Extract policy statements
        policy_keywords = ['policy', 'rule', 'regulation', 'procedure', 'guideline']
        
        doc1_policies = [s for s in doc1_sentences 
                        if any(keyword in s.lower() for keyword in policy_keywords)]
        doc2_policies = [s for s in doc2_sentences 
                        if any(keyword in s.lower() for keyword in policy_keywords)]
        
        # Compare policy statements
        for policy1 in doc1_policies:
            for policy2 in doc2_policies:
                similarity = self._calculate_context_similarity(policy1, policy2)
                
                if similarity > 0.7:  # Similar policy topics
                    # Check if they contradict each other
                    if self._are_policies_contradictory(policy1, policy2):
                        contradictions.append({
                            'type': 'policy',
                            'subtype': 'conflicting_policies',
                            'document1': doc1_name,
                            'document2': doc2_name,
                            'sentence1': policy1,
                            'sentence2': policy2,
                            'similarity': similarity,
                            'severity_score': 0.85,
                            'description': 'Conflicting policy statements found',
                            'suggestion': 'Harmonize the conflicting policies'
                        })
        
        return contradictions
    
    def _are_policies_contradictory(self, policy1: str, policy2: str) -> bool:
        """Check if two policy statements are contradictory"""
        # Simple contradiction detection based on keywords
        contradictory_pairs = [
            (['allow', 'permit', 'enable'], ['forbid', 'prohibit', 'disable', 'prevent']),
            (['require', 'mandatory', 'must'], ['optional', 'voluntary', 'may']),
            (['include', 'add'], ['exclude', 'remove', 'eliminate']),
        ]
        
        policy1_lower = policy1.lower()
        policy2_lower = policy2.lower()
        
        for positive_words, negative_words in contradictory_pairs:
            has_positive1 = any(word in policy1_lower for word in positive_words)
            has_negative1 = any(word in policy1_lower for word in negative_words)
            has_positive2 = any(word in policy2_lower for word in positive_words)
            has_negative2 = any(word in policy2_lower for word in negative_words)
            
            if (has_positive1 and has_negative2) or (has_negative1 and has_positive2):
                return True
        
        return False
