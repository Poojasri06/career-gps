"""
Skill Extractor Service
Extracts and normalizes skills from user input text
"""
from utils.embeddings import normalize_text, extract_skills_from_text
import pandas as pd
import re

class SkillExtractor:
    """Extracts skills from user text input"""
    
    def __init__(self, skills_df):
        self.skills_df = skills_df
        self.known_skills = skills_df['skill_name'].tolist()
    
    def extract_from_text(self, text):
        """
        Extract skills from free-form text
        Returns list of identified skills
        """
        if not text:
            return []
        
        # Use embeddings utility
        matched_skills = extract_skills_from_text(text, self.known_skills)
        
        # Additional pattern-based extraction
        additional_skills = self._pattern_based_extraction(text)
        
        # Combine and deduplicate
        all_skills = list(set(matched_skills + additional_skills))
        
        return all_skills
    
    def _pattern_based_extraction(self, text):
        """Extract skills using pattern matching"""
        extracted = []
        text_lower = text.lower()
        
        for skill in self.known_skills:
            skill_lower = skill.lower()
            
            # Check for variations
            patterns = [
                rf'\b{re.escape(skill_lower)}\b',
                rf'\b{re.escape(skill_lower)}s\b',  # Plural
                rf'\b{re.escape(skill_lower)}ing\b',  # -ing form
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    extracted.append(skill)
                    break
        
        return extracted
    
    def extract_from_list(self, skills_list):
        """
        Extract skills from comma-separated string or list
        Returns normalized list of skills
        """
        if isinstance(skills_list, str):
            skills = [s.strip() for s in skills_list.split(',')]
        else:
            skills = skills_list
        
        normalized_skills = []
        
        for skill in skills:
            # Try to match with known skills
            matched = self._match_to_known_skill(skill)
            if matched:
                normalized_skills.append(matched)
            else:
                # Add as-is if not found
                normalized_skills.append(skill)
        
        return list(set(normalized_skills))
    
    def _match_to_known_skill(self, skill):
        """Match user skill to known skill in database"""
        skill_normalized = normalize_text(skill)
        
        for known_skill in self.known_skills:
            known_normalized = normalize_text(known_skill)
            
            # Exact match
            if skill_normalized == known_normalized:
                return known_skill
            
            # Contains match
            if skill_normalized in known_normalized or known_normalized in skill_normalized:
                return known_skill
        
        return None
    
    def categorize_skills(self, skills):
        """
        Categorize skills by their category
        Returns dict of {category: [skills]}
        """
        categorized = {}
        
        for skill in skills:
            skill_info = self.skills_df[self.skills_df['skill_name'] == skill]
            
            if not skill_info.empty:
                category = skill_info.iloc[0]['category']
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(skill)
            else:
                if 'Other' not in categorized:
                    categorized['Other'] = []
                categorized['Other'].append(skill)
        
        return categorized
    
    def get_skill_info(self, skill_name):
        """Get detailed information about a skill"""
        skill_info = self.skills_df[self.skills_df['skill_name'] == skill_name]
        
        if skill_info.empty:
            return None
        
        row = skill_info.iloc[0]
        return {
            'name': row['skill_name'],
            'category': row['category'],
            'difficulty': row['difficulty'],
            'learning_time_weeks': row['learning_time_weeks'],
            'prerequisites': row['prerequisites'] if pd.notna(row['prerequisites']) else None
        }
