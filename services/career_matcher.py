"""
Career Matcher Service
Matches user profile with suitable career roles
"""
from utils.embeddings import SkillEmbedder, compute_skill_overlap
from utils.helpers import parse_skills_list, parse_importance_weights
import pandas as pd
import numpy as np

class CareerMatcher:
    """Matches users with career roles based on skills and interests"""
    
    def __init__(self, careers_df):
        self.careers_df = careers_df
        self.embedder = SkillEmbedder()
        self._prepare_career_embeddings()
    
    def _prepare_career_embeddings(self):
        """Prepare career descriptions for matching"""
        # Create combined text for each career
        career_texts = []
        for _, row in self.careers_df.iterrows():
            text = f"{row['role_name']} {row['category']} {row['description']} {row['required_skills']}"
            career_texts.append(text)
        
        # Fit embedder on career corpus
        self.career_embeddings = self.embedder.fit_transform(career_texts)
        self.career_texts = career_texts
    
    def match_careers(self, user_skills, user_interests=None, top_n=5):
        """
        Match user with top N careers
        Returns list of career matches with scores
        """
        # Create user profile text
        user_text = " ".join(user_skills)
        if user_interests:
            user_text += " " + user_interests
        
        # Get similarities
        similarities = self.embedder.get_similarities(user_text, self.career_texts)
        
        # Get top N matches
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        matches = []
        for idx in top_indices:
            career = self.careers_df.iloc[idx]
            required_skills = parse_skills_list(career['required_skills'])
            
            # Calculate skill overlap
            matched, partial, missing, overlap_score = compute_skill_overlap(
                user_skills, required_skills
            )
            
            # Combine similarity and overlap for final score
            final_score = (similarities[idx] * 0.4 + overlap_score * 0.6)
            
            matches.append({
                'role_id': career['role_id'],
                'role_name': career['role_name'],
                'category': career['category'],
                'description': career['description'],
                'match_score': final_score * 100,
                'similarity_score': similarities[idx] * 100,
                'skill_overlap_score': overlap_score * 100,
                'required_skills': required_skills,
                'matched_skills': matched,
                'partial_skills': partial,
                'missing_skills': missing,
                'importance_weights': parse_importance_weights(career['importance_weights']),
                'avg_salary': career['avg_salary'],
                'growth_rate': career['growth_rate']
            })
        
        return matches
    
    def get_career_details(self, role_id):
        """Get detailed information about a specific career role"""
        career = self.careers_df[self.careers_df['role_id'] == role_id]
        
        if career.empty:
            return None
        
        row = career.iloc[0]
        return {
            'role_id': row['role_id'],
            'role_name': row['role_name'],
            'category': row['category'],
            'description': row['description'],
            'required_skills': parse_skills_list(row['required_skills']),
            'importance_weights': parse_importance_weights(row['importance_weights']),
            'avg_salary': row['avg_salary'],
            'growth_rate': row['growth_rate']
        }
    
    def filter_by_category(self, category):
        """Get all careers in a specific category"""
        filtered = self.careers_df[self.careers_df['category'] == category]
        return filtered.to_dict('records')
    
    def get_similar_careers(self, role_id, top_n=3):
        """Find similar career paths to a given role"""
        career = self.get_career_details(role_id)
        
        if not career:
            return []
        
        # Create career text
        career_text = f"{career['role_name']} {career['category']} {' '.join(career['required_skills'])}"
        
        # Get similarities with all careers
        similarities = self.embedder.get_similarities(career_text, self.career_texts)
        
        # Get top N (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:top_n+1]
        
        similar_careers = []
        for idx in top_indices:
            similar_career = self.careers_df.iloc[idx]
            similar_careers.append({
                'role_id': similar_career['role_id'],
                'role_name': similar_career['role_name'],
                'category': similar_career['category'],
                'similarity': similarities[idx] * 100
            })
        
        return similar_careers
