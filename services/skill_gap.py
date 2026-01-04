"""
Skill Gap Analyzer Service
Analyzes skill gaps for target career roles
"""
from utils.embeddings import compute_skill_overlap
from utils.helpers import parse_skills_list, parse_importance_weights, estimate_learning_time
import pandas as pd

class SkillGapAnalyzer:
    """Analyzes skill gaps between user skills and career requirements"""
    
    def __init__(self, skills_df):
        self.skills_df = skills_df
    
    def analyze_gap(self, user_skills, career_match):
        """
        Analyze skill gap for a specific career
        Returns detailed gap analysis
        """
        required_skills = career_match['required_skills']
        importance_weights_list = career_match.get('importance_weights', [])
        
        # Create importance weights dict
        importance_weights = {}
        for i, skill in enumerate(required_skills):
            if i < len(importance_weights_list):
                importance_weights[skill] = importance_weights_list[i]
            else:
                importance_weights[skill] = 0.5  # Default weight
        
        # Compute overlap
        matched, partial, missing, overlap_score = compute_skill_overlap(
            user_skills, required_skills
        )
        
        # Calculate weighted scores for each skill
        skill_details = []
        for skill in required_skills:
            status = 'missing'
            coverage = 0.0
            
            if skill in matched:
                status = 'known'
                coverage = 1.0
            elif skill in partial:
                status = 'partial'
                coverage = 0.5
            
            weight = importance_weights.get(skill, 0.5)
            skill_info = self._get_skill_learning_info(skill)
            
            skill_details.append({
                'skill': skill,
                'status': status,
                'coverage': coverage,
                'importance': weight,
                'weighted_score': coverage * weight,
                'learning_time_weeks': skill_info['learning_time_weeks'],
                'difficulty': skill_info['difficulty'],
                'prerequisites': skill_info['prerequisites']
            })
        
        # Sort by importance (descending)
        skill_details.sort(key=lambda x: x['importance'], reverse=True)
        
        # Estimate learning time
        learning_time_weeks = estimate_learning_time(missing, partial, self.skills_df)
        
        # Calculate gap percentage
        gap_percentage = (len(missing) + 0.5 * len(partial)) / len(required_skills) * 100
        
        return {
            'career_name': career_match['role_name'],
            'total_required_skills': len(required_skills),
            'known_skills_count': len(matched),
            'partial_skills_count': len(partial),
            'missing_skills_count': len(missing),
            'overlap_percentage': overlap_score * 100,
            'gap_percentage': gap_percentage,
            'matched_skills': matched,
            'partial_skills': partial,
            'missing_skills': missing,
            'skill_details': skill_details,
            'estimated_learning_time_weeks': learning_time_weeks,
            'priority_skills': self._get_priority_skills(skill_details)
        }
    
    def _get_skill_learning_info(self, skill_name):
        """Get learning information for a skill"""
        skill_info = self.skills_df[self.skills_df['skill_name'] == skill_name]
        
        if skill_info.empty:
            return {
                'learning_time_weeks': 4,
                'difficulty': 'intermediate',
                'prerequisites': None
            }
        
        row = skill_info.iloc[0]
        learning_time = row['learning_time_weeks']
        
        if pd.isna(learning_time) or learning_time == 'continuous':
            learning_time = 4
        
        return {
            'learning_time_weeks': float(learning_time),
            'difficulty': row['difficulty'],
            'prerequisites': row['prerequisites'] if pd.notna(row['prerequisites']) else None
        }
    
    def _get_priority_skills(self, skill_details):
        """
        Identify priority skills to learn first
        Based on: high importance, not known, and no unmet prerequisites
        """
        priority = []
        
        for skill in skill_details:
            if skill['status'] == 'missing' and skill['importance'] >= 0.7:
                # Check prerequisites
                prereqs = skill['prerequisites']
                if not prereqs or pd.isna(prereqs):
                    priority.append(skill['skill'])
                else:
                    # Check if prerequisites are met
                    prereq_list = [p.strip() for p in str(prereqs).split(',')]
                    prereqs_met = all(
                        any(s['skill'] == prereq and s['status'] == 'known' 
                            for s in skill_details)
                        for prereq in prereq_list
                    )
                    if prereqs_met:
                        priority.append(skill['skill'])
        
        return priority[:5]  # Top 5 priority skills
    
    def compare_careers(self, user_skills, career_matches):
        """
        Compare skill gaps across multiple careers
        Returns comparison data
        """
        comparisons = []
        
        for career in career_matches:
            gap_analysis = self.analyze_gap(user_skills, career)
            
            comparisons.append({
                'career_name': career['role_name'],
                'match_score': career['match_score'],
                'gap_percentage': gap_analysis['gap_percentage'],
                'missing_count': gap_analysis['missing_skills_count'],
                'learning_time_weeks': gap_analysis['estimated_learning_time_weeks'],
                'priority_skills': gap_analysis['priority_skills']
            })
        
        return comparisons
    
    def get_learning_path(self, skill_details):
        """
        Create optimal learning path considering prerequisites
        Returns ordered list of skills to learn
        """
        learning_path = []
        known_skills = [s['skill'] for s in skill_details if s['status'] == 'known']
        
        # Skills to learn (missing + partial)
        to_learn = [s for s in skill_details if s['status'] in ['missing', 'partial']]
        
        # Sort by importance and difficulty
        to_learn.sort(key=lambda x: (x['importance'], -ord(x['difficulty'][0])), reverse=True)
        
        while to_learn:
            added = False
            
            for skill in to_learn:
                prereqs = skill['prerequisites']
                
                # Check if prerequisites are met
                if not prereqs or pd.isna(prereqs):
                    learning_path.append(skill)
                    known_skills.append(skill['skill'])
                    to_learn.remove(skill)
                    added = True
                    break
                else:
                    prereq_list = [p.strip() for p in str(prereqs).split(',')]
                    if all(prereq in known_skills for prereq in prereq_list):
                        learning_path.append(skill)
                        known_skills.append(skill['skill'])
                        to_learn.remove(skill)
                        added = True
                        break
            
            # If no skill can be added (circular dependencies or missing prereqs), add next anyway
            if not added and to_learn:
                learning_path.append(to_learn[0])
                known_skills.append(to_learn[0]['skill'])
                to_learn.pop(0)
        
        return learning_path
