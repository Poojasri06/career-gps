"""
Embeddings utility for text representation using TF-IDF and Sentence Transformers
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class SkillEmbedder:
    """Creates embeddings for skills and text using TF-IDF"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            lowercase=True,
            stop_words='english'
        )
        self.is_fitted = False
    
    def fit(self, texts):
        """Fit the vectorizer on a corpus of texts"""
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self
    
    def transform(self, texts):
        """Transform texts into embeddings"""
        if not self.is_fitted:
            raise ValueError("Embedder must be fitted first")
        
        if isinstance(texts, str):
            texts = [texts]
        
        return self.vectorizer.transform(texts)
    
    def fit_transform(self, texts):
        """Fit and transform in one step"""
        if isinstance(texts, str):
            texts = [texts]
        
        self.is_fitted = True
        return self.vectorizer.fit_transform(texts)
    
    def get_similarity(self, text1, text2):
        """Calculate cosine similarity between two texts"""
        if not self.is_fitted:
            # Fit on both texts combined
            self.fit([text1, text2])
        
        vec1 = self.transform([text1])
        vec2 = self.transform([text2])
        
        return cosine_similarity(vec1, vec2)[0][0]
    
    def get_similarities(self, query, corpus):
        """Calculate similarities between a query and a corpus of texts"""
        if not self.is_fitted:
            # Fit on corpus
            self.fit(corpus)
        
        query_vec = self.transform([query])
        corpus_vecs = self.transform(corpus)
        
        similarities = cosine_similarity(query_vec, corpus_vecs)[0]
        return similarities


def normalize_text(text):
    """Normalize text for better matching"""
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces and commas
    text = re.sub(r'[^a-z0-9\s,]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def extract_skills_from_text(text, known_skills):
    """
    Extract skills from text by matching with known skills
    Returns list of matched skills
    """
    if not text:
        return []
    
    text_normalized = normalize_text(text)
    matched_skills = []
    
    for skill in known_skills:
        skill_normalized = normalize_text(skill)
        
        # Exact match or contains
        if skill_normalized in text_normalized or text_normalized in skill_normalized:
            matched_skills.append(skill)
    
    return matched_skills


def compute_skill_overlap(user_skills, required_skills):
    """
    Compute overlap between user skills and required skills
    Returns: (matched_skills, partial_skills, missing_skills, overlap_score)
    """
    user_skills_normalized = [normalize_text(s) for s in user_skills]
    required_skills_normalized = [normalize_text(s) for s in required_skills]
    
    matched = []
    partial = []
    missing = []
    
    for req_skill in required_skills:
        req_normalized = normalize_text(req_skill)
        exact_match = False
        partial_match = False
        
        for user_skill in user_skills:
            user_normalized = normalize_text(user_skill)
            
            # Exact match
            if req_normalized == user_normalized:
                matched.append(req_skill)
                exact_match = True
                break
            
            # Partial match (contains)
            if req_normalized in user_normalized or user_normalized in req_normalized:
                partial_match = True
        
        if not exact_match:
            if partial_match:
                partial.append(req_skill)
            else:
                missing.append(req_skill)
    
    # Calculate overlap score
    overlap_score = (len(matched) + 0.5 * len(partial)) / len(required_skills) if required_skills else 0
    
    return matched, partial, missing, overlap_score
