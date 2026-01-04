"""
Career Readiness Score Calculator
Calculates and updates career readiness scores dynamically
"""
import numpy as np
from utils.helpers import calculate_weighted_score

class ReadinessScoreCalculator:
    """Calculates career readiness score based on multiple factors"""
    
    def __init__(self):
        # Weights for different components of readiness score
        self.weights = {
            'skill_coverage': 0.5,      # How many skills are covered
            'skill_importance': 0.25,   # Coverage of important skills
            'skill_depth': 0.15,        # Depth of knowledge (partial vs full)
            'learning_consistency': 0.1  # Simulated learning behavior
        }
    
    def calculate_score(self, gap_analysis, learning_progress=None):
        """
        Calculate comprehensive readiness score (0-100)
        
        Args:
            gap_analysis: Result from SkillGapAnalyzer
            learning_progress: Optional dict with learning metrics
        
        Returns:
            dict with score and breakdown
        """
        # Component 1: Skill Coverage Score
        total_skills = gap_analysis['total_required_skills']
        known_skills = gap_analysis['known_skills_count']
        partial_skills = gap_analysis['partial_skills_count']
        
        coverage_score = ((known_skills + 0.5 * partial_skills) / total_skills) * 100
        
        # Component 2: Skill Importance Score
        # Calculate weighted score based on importance weights
        skill_coverage_dict = {}
        for skill_detail in gap_analysis['skill_details']:
            skill_coverage_dict[skill_detail['skill']] = skill_detail['coverage']
        
        importance_weights = {
            skill_detail['skill']: skill_detail['importance']
            for skill_detail in gap_analysis['skill_details']
        }
        
        importance_score = calculate_weighted_score(skill_coverage_dict, importance_weights)
        
        # Component 3: Skill Depth Score
        # Reward full mastery over partial knowledge
        depth_score = (known_skills / total_skills) * 100 if total_skills > 0 else 0
        
        # Component 4: Learning Consistency Score (simulated or provided)
        if learning_progress and 'consistency_score' in learning_progress:
            consistency_score = learning_progress['consistency_score']
        else:
            # Simulate based on current progress
            consistency_score = min(coverage_score * 0.8 + 20, 100)
        
        # Calculate weighted final score
        final_score = (
            coverage_score * self.weights['skill_coverage'] +
            importance_score * self.weights['skill_importance'] +
            depth_score * self.weights['skill_depth'] +
            consistency_score * self.weights['learning_consistency']
        )
        
        return {
            'overall_score': round(final_score, 1),
            'breakdown': {
                'skill_coverage': round(coverage_score, 1),
                'skill_importance': round(importance_score, 1),
                'skill_depth': round(depth_score, 1),
                'learning_consistency': round(consistency_score, 1)
            },
            'grade': self._get_grade(final_score),
            'interpretation': self._interpret_score(final_score)
        }
    
    def _get_grade(self, score):
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _interpret_score(self, score):
        """Provide interpretation of the readiness score"""
        if score >= 85:
            return "Excellent! You're highly prepared for this career path."
        elif score >= 70:
            return "Good progress! Focus on remaining gaps to strengthen readiness."
        elif score >= 55:
            return "Moderate readiness. Consistent learning will improve your position."
        elif score >= 40:
            return "Early stage. Significant learning needed, but achievable with focus."
        else:
            return "Beginning journey. Consider building foundational skills first."
    
    def update_score_after_simulation(self, current_score_data, simulation_changes):
        """
        Update readiness score after a what-if simulation
        
        Args:
            current_score_data: Current score breakdown
            simulation_changes: Dict describing changes (e.g., skills added/removed)
        
        Returns:
            Updated score data
        """
        # Extract current breakdown
        breakdown = current_score_data['breakdown']
        
        # Apply changes from simulation
        if 'skill_coverage_change' in simulation_changes:
            breakdown['skill_coverage'] += simulation_changes['skill_coverage_change']
            breakdown['skill_coverage'] = max(0, min(100, breakdown['skill_coverage']))
        
        if 'skill_depth_change' in simulation_changes:
            breakdown['skill_depth'] += simulation_changes['skill_depth_change']
            breakdown['skill_depth'] = max(0, min(100, breakdown['skill_depth']))
        
        if 'consistency_change' in simulation_changes:
            breakdown['learning_consistency'] += simulation_changes['consistency_change']
            breakdown['learning_consistency'] = max(0, min(100, breakdown['learning_consistency']))
        
        # Recalculate overall score
        new_overall = (
            breakdown['skill_coverage'] * self.weights['skill_coverage'] +
            breakdown['skill_importance'] * self.weights['skill_importance'] +
            breakdown['skill_depth'] * self.weights['skill_depth'] +
            breakdown['learning_consistency'] * self.weights['learning_consistency']
        )
        
        return {
            'overall_score': round(new_overall, 1),
            'breakdown': breakdown,
            'grade': self._get_grade(new_overall),
            'interpretation': self._interpret_score(new_overall),
            'change_from_baseline': round(new_overall - current_score_data['overall_score'], 1)
        }
    
    def compare_scores(self, scores_list):
        """
        Compare multiple career readiness scores
        Returns ranked list with recommendations
        """
        ranked = sorted(scores_list, key=lambda x: x['overall_score'], reverse=True)
        
        for i, score_data in enumerate(ranked):
            score_data['rank'] = i + 1
            if i == 0:
                score_data['recommendation'] = "Top Match - Strongest readiness"
            elif score_data['overall_score'] >= 70:
                score_data['recommendation'] = "Strong Alternative"
            elif score_data['overall_score'] >= 50:
                score_data['recommendation'] = "Viable with Learning"
            else:
                score_data['recommendation'] = "Long-term Goal"
        
        return ranked
    
    def get_improvement_suggestions(self, score_data, gap_analysis):
        """Generate suggestions to improve readiness score"""
        suggestions = []
        breakdown = score_data['breakdown']
        
        # Analyze weakest areas
        weak_areas = sorted(
            breakdown.items(),
            key=lambda x: x[1]
        )
        
        for area, score in weak_areas[:2]:  # Focus on 2 weakest areas
            if area == 'skill_coverage':
                suggestions.append({
                    'area': 'Skill Coverage',
                    'current_score': score,
                    'suggestion': f"Focus on learning {len(gap_analysis['missing_skills'])} missing skills",
                    'priority_skills': gap_analysis['priority_skills'][:3],
                    'potential_improvement': '+15-25 points'
                })
            elif area == 'skill_importance':
                high_importance_missing = [
                    s for s in gap_analysis['skill_details']
                    if s['status'] == 'missing' and s['importance'] >= 0.7
                ]
                suggestions.append({
                    'area': 'Critical Skills',
                    'current_score': score,
                    'suggestion': f"Prioritize {len(high_importance_missing)} high-importance skills",
                    'priority_skills': [s['skill'] for s in high_importance_missing[:3]],
                    'potential_improvement': '+20-30 points'
                })
            elif area == 'skill_depth':
                suggestions.append({
                    'area': 'Skill Mastery',
                    'current_score': score,
                    'suggestion': f"Deepen knowledge in {len(gap_analysis['partial_skills'])} partial skills",
                    'priority_skills': gap_analysis['partial_skills'][:3],
                    'potential_improvement': '+10-15 points'
                })
            elif area == 'learning_consistency':
                suggestions.append({
                    'area': 'Learning Consistency',
                    'current_score': score,
                    'suggestion': "Maintain regular learning schedule and track progress",
                    'priority_skills': [],
                    'potential_improvement': '+5-10 points'
                })
        
        return suggestions
