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
        
        score_data = {
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

        # Add human-readable explanation (why + next steps)
        try:
            score_data['explanation'] = self.generate_explanation(score_data, gap_analysis)
        except Exception:
            score_data['explanation'] = score_data['interpretation']

        return score_data
    
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
    
    def update_score_after_simulation(self, current_score_data, simulation_changes, gap_analysis=None):
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
        
        updated = {
            'overall_score': round(new_overall, 1),
            'breakdown': breakdown,
            'grade': self._get_grade(new_overall),
            'interpretation': self._interpret_score(new_overall),
            'change_from_baseline': round(new_overall - current_score_data['overall_score'], 1)
        }

        try:
            # If gap analysis provided, produce an explanation using latest gaps
            updated['explanation'] = self.generate_explanation(updated, gap_analysis or {})
        except Exception:
            updated['explanation'] = updated['interpretation']

        return updated

    def generate_explanation(self, score_data, gap_analysis):
        """Produce a concise human-readable explanation: why the score is at this level and next steps."""
        parts = []

        # Why: primary drivers
        breakdown = score_data.get('breakdown', {})
        if breakdown:
            sorted_drivers = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            top = sorted_drivers[0][0] if sorted_drivers else None
            parts.append(f"Why: Top contributor is {top.replace('_', ' ')} ({breakdown.get(top, 0):.0f}%).")

        # Mention important missing skills if available
        missing = gap_analysis.get('missing_skills', []) if isinstance(gap_analysis, dict) else []
        priority = gap_analysis.get('priority_skills', []) if isinstance(gap_analysis, dict) else []
        if priority:
            parts.append(f"Next steps: Prioritize {', '.join(priority[:3])} to reduce critical gaps.")
        elif missing:
            parts.append(f"Next steps: Learn {missing[:3]} to improve coverage.")

        # Give a short path forward based on weakest area
        weakest = sorted(breakdown.items(), key=lambda x: x[1])[0][0] if breakdown else None
        if weakest == 'skill_coverage':
            parts.append("Focus on learning missing skills and converting partial skills to known.")
        elif weakest == 'skill_depth':
            parts.append("Deepen mastery with projects and practical exercises for partial skills.")
        elif weakest == 'skill_importance':
            parts.append("Prioritize high-importance skills that employers expect.")
        elif weakest == 'learning_consistency':
            parts.append("Establish a steady learning schedule and track small wins.")

        # Combine
        explanation = ' '.join(parts)
        return explanation
    
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
