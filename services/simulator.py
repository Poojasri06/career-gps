"""
Career Simulation Engine - CORE DIFFERENTIATOR
Allows users to simulate what-if career scenarios and see real-time impact
"""
import copy
from services.skill_gap import SkillGapAnalyzer
from services.readiness_score import ReadinessScoreCalculator
from utils.helpers import estimate_learning_time, calculate_risk_level

class CareerSimulator:
    """
    What-If Career Simulation Engine
    Simulates career decisions and dynamically updates recommendations
    """
    
    def __init__(self, skills_df):
        self.skills_df = skills_df
        self.gap_analyzer = SkillGapAnalyzer(skills_df)
        self.score_calculator = ReadinessScoreCalculator()
    
    def create_baseline(self, user_skills, career_match):
        """
        Create baseline state for simulation
        Returns initial state with all metrics
        """
        gap_analysis = self.gap_analyzer.analyze_gap(user_skills, career_match)
        readiness_score = self.score_calculator.calculate_score(gap_analysis)
        
        baseline = {
            'user_skills': user_skills.copy(),
            'career': career_match['role_name'],
            'gap_analysis': gap_analysis,
            'readiness_score': readiness_score,
            'learning_time_weeks': gap_analysis['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                readiness_score['overall_score'],
                gap_analysis['gap_percentage']
            )
        }
        
        return baseline
    
    def simulate_switch_career(self, baseline, new_career_match):
        """
        Simulate switching to a different career role
        """
        user_skills = baseline['user_skills']
        
        # Analyze new career
        new_gap_analysis = self.gap_analyzer.analyze_gap(user_skills, new_career_match)
        new_readiness_score = self.score_calculator.calculate_score(new_gap_analysis)
        
        simulation_result = {
            'simulation_type': 'Switch Career',
            'from_career': baseline['career'],
            'to_career': new_career_match['role_name'],
            'user_skills': user_skills,
            'gap_analysis': new_gap_analysis,
            'readiness_score': new_readiness_score,
            'learning_time_weeks': new_gap_analysis['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                new_readiness_score['overall_score'],
                new_gap_analysis['gap_percentage']
            ),
            'changes': {
                'score_change': new_readiness_score['overall_score'] - baseline['readiness_score']['overall_score'],
                'time_change': new_gap_analysis['estimated_learning_time_weeks'] - baseline['learning_time_weeks'],
                'gap_change': new_gap_analysis['gap_percentage'] - baseline['gap_analysis']['gap_percentage'],
                'new_missing_skills': list(set(new_gap_analysis['missing_skills']) - set(baseline['gap_analysis']['missing_skills'])),
                'removed_requirements': list(set(baseline['gap_analysis']['missing_skills']) - set(new_gap_analysis['missing_skills']))
            }
        }
        
        return simulation_result
    
    def simulate_skip_certifications(self, baseline, certification_skills):
        """
        Simulate removing certification-based skills from requirements
        (Assumes certifications are specific skills like AWS, Azure certifications)
        """
        # Create modified career requirements
        modified_gap = copy.deepcopy(baseline['gap_analysis'])
        
        # Remove certification skills from missing
        original_missing = modified_gap['missing_skills'].copy()
        modified_gap['missing_skills'] = [
            s for s in modified_gap['missing_skills']
            if s not in certification_skills
        ]
        
        # Recalculate metrics
        total_skills = modified_gap['total_required_skills']
        known = modified_gap['known_skills_count']
        partial = modified_gap['partial_skills_count']
        missing = len(modified_gap['missing_skills'])
        
        modified_gap['missing_skills_count'] = missing
        modified_gap['gap_percentage'] = (missing + 0.5 * partial) / total_skills * 100
        modified_gap['overlap_percentage'] = 100 - modified_gap['gap_percentage']
        
        # Recalculate learning time
        modified_gap['estimated_learning_time_weeks'] = estimate_learning_time(
            modified_gap['missing_skills'],
            modified_gap['partial_skills'],
            self.skills_df
        )
        
        # Recalculate readiness score with penalty for skipping certifications
        simulation_changes = {
            'skill_coverage_change': 10,  # Boost from fewer requirements
            'skill_depth_change': -5,     # Penalty for skipping depth
            'consistency_change': -3      # Small consistency penalty
        }
        
        modified_score = self.score_calculator.update_score_after_simulation(
            baseline['readiness_score'],
            simulation_changes
        )
        
        simulation_result = {
            'simulation_type': 'Skip Certifications',
            'career': baseline['career'],
            'user_skills': baseline['user_skills'],
            'skipped_certifications': certification_skills,
            'gap_analysis': modified_gap,
            'readiness_score': modified_score,
            'learning_time_weeks': modified_gap['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                modified_score['overall_score'],
                modified_gap['gap_percentage']
            ),
            'changes': {
                'score_change': modified_score['change_from_baseline'],
                'time_change': modified_gap['estimated_learning_time_weeks'] - baseline['learning_time_weeks'],
                'gap_change': modified_gap['gap_percentage'] - baseline['gap_analysis']['gap_percentage'],
                'removed_skills': list(set(original_missing) - set(modified_gap['missing_skills']))
            },
            'warning': 'Skipping certifications may reduce competitiveness in job market'
        }
        
        return simulation_result
    
    def simulate_focus_projects(self, baseline, project_skills):
        """
        Simulate focusing on project-based learning (practical skills)
        Boosts practical skills but may miss theoretical depth
        """
        modified_gap = copy.deepcopy(baseline['gap_analysis'])
        
        # Convert partial project skills to known
        newly_mastered = []
        for skill in project_skills:
            if skill in modified_gap['partial_skills']:
                modified_gap['partial_skills'].remove(skill)
                modified_gap['matched_skills'].append(skill)
                newly_mastered.append(skill)
        
        # Update counts
        modified_gap['known_skills_count'] = len(modified_gap['matched_skills'])
        modified_gap['partial_skills_count'] = len(modified_gap['partial_skills'])
        modified_gap['gap_percentage'] = (
            (modified_gap['missing_skills_count'] + 0.5 * modified_gap['partial_skills_count']) /
            modified_gap['total_required_skills'] * 100
        )
        
        # Reduce learning time (projects are more efficient)
        modified_gap['estimated_learning_time_weeks'] = baseline['learning_time_weeks'] * 0.75
        
        # Calculate new score with project boost
        simulation_changes = {
            'skill_coverage_change': len(newly_mastered) * 3,
            'skill_depth_change': 5,      # Project boost
            'consistency_change': 5       # Hands-on learning boost
        }
        
        modified_score = self.score_calculator.update_score_after_simulation(
            baseline['readiness_score'],
            simulation_changes
        )
        
        simulation_result = {
            'simulation_type': 'Focus on Projects',
            'career': baseline['career'],
            'user_skills': baseline['user_skills'] + newly_mastered,
            'project_focus_skills': project_skills,
            'newly_mastered': newly_mastered,
            'gap_analysis': modified_gap,
            'readiness_score': modified_score,
            'learning_time_weeks': modified_gap['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                modified_score['overall_score'],
                modified_gap['gap_percentage']
            ),
            'changes': {
                'score_change': modified_score['change_from_baseline'],
                'time_change': modified_gap['estimated_learning_time_weeks'] - baseline['learning_time_weeks'],
                'gap_change': modified_gap['gap_percentage'] - baseline['gap_analysis']['gap_percentage'],
                'skills_improved': newly_mastered
            },
            'benefit': 'Project-based learning accelerates practical skill development'
        }
        
        return simulation_result
    
    def simulate_pause_learning(self, baseline, pause_weeks):
        """
        Simulate pausing learning for a period
        Shows impact of delay on timeline and score decay
        """
        modified_gap = copy.deepcopy(baseline['gap_analysis'])
        
        # Add pause to learning time
        modified_gap['estimated_learning_time_weeks'] = baseline['learning_time_weeks'] + pause_weeks
        
        # Simulate skill decay (small penalty for pausing)
        decay_penalty = min(pause_weeks * 0.5, 10)  # Max 10 point decay
        
        simulation_changes = {
            'skill_coverage_change': 0,
            'skill_depth_change': -decay_penalty * 0.6,
            'consistency_change': -decay_penalty * 0.4
        }
        
        modified_score = self.score_calculator.update_score_after_simulation(
            baseline['readiness_score'],
            simulation_changes
        )
        
        simulation_result = {
            'simulation_type': 'Pause Learning',
            'career': baseline['career'],
            'user_skills': baseline['user_skills'],
            'pause_duration_weeks': pause_weeks,
            'gap_analysis': modified_gap,
            'readiness_score': modified_score,
            'learning_time_weeks': modified_gap['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                modified_score['overall_score'],
                modified_gap['gap_percentage']
            ),
            'changes': {
                'score_change': modified_score['change_from_baseline'],
                'time_change': pause_weeks,
                'gap_change': 0,  # Gap doesn't change, just timeline
                'decay_penalty': decay_penalty
            },
            'warning': f'Pausing for {pause_weeks} weeks may cause skill decay and delay career readiness'
        }
        
        return simulation_result
    
    def simulate_add_skills(self, baseline, new_skills, career_match):
        """
        Simulate what happens if user learns specific new skills
        """
        modified_user_skills = baseline['user_skills'] + new_skills
        
        # Re-analyze with new skills
        modified_gap = self.gap_analyzer.analyze_gap(modified_user_skills, career_match)
        modified_score = self.score_calculator.calculate_score(modified_gap)
        
        simulation_result = {
            'simulation_type': 'Add Skills',
            'career': baseline['career'],
            'user_skills': modified_user_skills,
            'newly_added_skills': new_skills,
            'gap_analysis': modified_gap,
            'readiness_score': modified_score,
            'learning_time_weeks': modified_gap['estimated_learning_time_weeks'],
            'risk_level': calculate_risk_level(
                modified_score['overall_score'],
                modified_gap['gap_percentage']
            ),
            'changes': {
                'score_change': modified_score['overall_score'] - baseline['readiness_score']['overall_score'],
                'time_change': modified_gap['estimated_learning_time_weeks'] - baseline['learning_time_weeks'],
                'gap_change': modified_gap['gap_percentage'] - baseline['gap_analysis']['gap_percentage'],
                'skills_moved_to_known': [s for s in new_skills if s in modified_gap['matched_skills']]
            },
            'benefit': f'Adding {len(new_skills)} skills improves readiness significantly'
        }
        
        return simulation_result
    
    def compare_simulations(self, simulations):
        """
        Compare multiple simulation results
        Returns ranked comparison with recommendations
        """
        comparison = []
        
        for sim in simulations:
            comparison.append({
                'simulation_type': sim['simulation_type'],
                'readiness_score': sim['readiness_score']['overall_score'],
                'score_change': sim['changes']['score_change'],
                'time_weeks': sim['learning_time_weeks'],
                'time_change': sim['changes']['time_change'],
                'risk_level': sim['risk_level'],
                'gap_percentage': sim['gap_analysis']['gap_percentage']
            })
        
        # Rank by readiness score
        comparison.sort(key=lambda x: x['readiness_score'], reverse=True)
        
        # Add recommendations
        for i, comp in enumerate(comparison):
            comp['rank'] = i + 1
            if i == 0:
                comp['recommendation'] = 'Best Overall Outcome'
            elif comp['time_change'] < 0:
                comp['recommendation'] = 'Fastest Path'
            elif comp['score_change'] > 5:
                comp['recommendation'] = 'Highest Score Gain'
            else:
                comp['recommendation'] = 'Consider Trade-offs'
        
        return comparison
