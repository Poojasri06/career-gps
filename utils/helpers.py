"""
Helper utility functions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data():
    """Load all CSV datasets"""
    try:
        careers_df = pd.read_csv('data/careers.csv')
        skills_df = pd.read_csv('data/skills.csv')
        resources_df = pd.read_csv('data/resources.csv')
        return careers_df, skills_df, resources_df
    except FileNotFoundError as e:
        raise Exception(f"Data file not found: {e}. Please ensure CSV files are in the 'data' folder.")


def parse_skills_list(skills_string):
    """Parse comma-separated skills string into list"""
    if pd.isna(skills_string) or not skills_string:
        return []
    return [s.strip() for s in str(skills_string).split(',')]


def parse_importance_weights(weights_string):
    """Parse comma-separated weights string into list of floats"""
    if pd.isna(weights_string) or not weights_string:
        return []
    return [float(w.strip()) for w in str(weights_string).split(',')]


def calculate_weighted_score(skills_coverage, importance_weights):
    """
    Calculate weighted score based on skill coverage and importance
    skills_coverage: dict of {skill: score} where score is 0 (missing), 0.5 (partial), 1 (known)
    importance_weights: dict of {skill: weight}
    """
    if not skills_coverage or not importance_weights:
        return 0.0
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for skill, coverage in skills_coverage.items():
        weight = importance_weights.get(skill, 0.5)  # Default weight if not found
        total_weighted_score += coverage * weight
        total_weight += weight
    
    return (total_weighted_score / total_weight * 100) if total_weight > 0 else 0.0


def estimate_learning_time(missing_skills, partial_skills, skills_df):
    """
    Estimate time needed to learn missing and partial skills
    Returns time in weeks
    """
    total_weeks = 0
    
    # Merge missing and partial (partial takes 50% time)
    all_skills = list(missing_skills) + list(partial_skills)
    
    for skill in missing_skills:
        skill_info = skills_df[skills_df['skill_name'].str.lower() == skill.lower()]
        if not skill_info.empty:
            weeks = skill_info.iloc[0]['learning_time_weeks']
            if pd.notna(weeks) and weeks != 'continuous':
                total_weeks += float(weeks)
            else:
                total_weeks += 4  # Default estimate
        else:
            total_weeks += 4  # Default estimate
    
    # Partial skills take half the time
    for skill in partial_skills:
        skill_info = skills_df[skills_df['skill_name'].str.lower() == skill.lower()]
        if not skill_info.empty:
            weeks = skill_info.iloc[0]['learning_time_weeks']
            if pd.notna(weeks) and weeks != 'continuous':
                total_weeks += float(weeks) * 0.5
            else:
                total_weeks += 2  # Default estimate
        else:
            total_weeks += 2  # Default estimate
    
    return total_weeks


def calculate_risk_level(readiness_score, skill_gap_percentage):
    """
    Calculate risk level based on readiness score and skill gap
    Returns: ('Low', 'Medium', 'High', 'Very High')
    """
    if readiness_score >= 80 and skill_gap_percentage <= 20:
        return 'Low'
    elif readiness_score >= 60 and skill_gap_percentage <= 40:
        return 'Medium'
    elif readiness_score >= 40 and skill_gap_percentage <= 60:
        return 'High'
    else:
        return 'Very High'


def get_skill_resources(skill_name, resources_df):
    """Get learning resources for a specific skill"""
    resources = resources_df[resources_df['skill_name'].str.lower() == skill_name.lower()]
    
    if resources.empty:
        return []
    
    resource_list = []
    for _, row in resources.iterrows():
        resource_list.append({
            'name': row['resource_name'],
            'type': row['resource_type'],
            'url': row['url'],
            'duration': row['duration_weeks'],
            'difficulty': row['difficulty']
        })
    
    return resource_list


def format_timeline_estimate(weeks):
    """Format weeks into readable timeline"""
    if weeks <= 4:
        return f"{int(weeks)} weeks (1 month)"
    elif weeks <= 12:
        months = weeks / 4
        return f"{int(weeks)} weeks ({months:.1f} months)"
    elif weeks <= 52:
        months = weeks / 4
        return f"{months:.1f} months"
    else:
        years = weeks / 52
        return f"{years:.1f} years"


def get_difficulty_color(difficulty):
    """Return color code for difficulty level"""
    colors = {
        'beginner': '#28a745',
        'intermediate': '#ffc107',
        'advanced': '#dc3545'
    }
    return colors.get(difficulty.lower(), '#6c757d')


def get_risk_color(risk_level):
    """Return color code for risk level"""
    colors = {
        'Low': '#28a745',
        'Medium': '#ffc107',
        'High': '#fd7e14',
        'Very High': '#dc3545'
    }
    return colors.get(risk_level, '#6c757d')


def create_weekly_plan(missing_skills, partial_skills, skills_df, weeks_per_phase=4):
    """
    Create a weekly learning plan
    Returns list of phases with skills to focus on
    """
    plan = []
    
    # Prioritize based on difficulty - start with beginner/intermediate
    all_learning_tasks = []
    
    for skill in missing_skills:
        skill_info = skills_df[skills_df['skill_name'].str.lower() == skill.lower()]
        difficulty = skill_info.iloc[0]['difficulty'] if not skill_info.empty else 'intermediate'
        priority = {'beginner': 1, 'intermediate': 2, 'advanced': 3}.get(difficulty, 2)
        all_learning_tasks.append({
            'skill': skill,
            'type': 'Learn',
            'priority': priority,
            'difficulty': difficulty
        })
    
    for skill in partial_skills:
        skill_info = skills_df[skills_df['skill_name'].str.lower() == skill.lower()]
        difficulty = skill_info.iloc[0]['difficulty'] if not skill_info.empty else 'intermediate'
        priority = {'beginner': 1, 'intermediate': 2, 'advanced': 3}.get(difficulty, 2)
        all_learning_tasks.append({
            'skill': skill,
            'type': 'Improve',
            'priority': priority,
            'difficulty': difficulty
        })
    
    # Sort by priority
    all_learning_tasks.sort(key=lambda x: x['priority'])
    
    # Group into phases
    phase_num = 1
    for i in range(0, len(all_learning_tasks), 3):  # 3 skills per phase
        phase_skills = all_learning_tasks[i:i+3]
        plan.append({
            'phase': phase_num,
            'duration_weeks': weeks_per_phase,
            'skills': phase_skills
        })
        phase_num += 1
    
    return plan
