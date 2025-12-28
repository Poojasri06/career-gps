"""
Daily Learning Plan Generator
Creates personalized daily learning plans based on user's goals and progress
"""
from datetime import datetime, timedelta
import random

class DailyLearningPlan:
    
    def __init__(self):
        self.activity_types = {
            'video': ['Watch tutorial video', 'View course lecture', 'Watch coding session'],
            'reading': ['Read documentation', 'Study article', 'Review book chapter'],
            'practice': ['Complete coding exercise', 'Build mini-project', 'Solve problems'],
            'project': ['Work on portfolio project', 'Implement feature', 'Debug and refine'],
            'review': ['Review concepts', 'Revisit previous work', 'Practice flashcards']
        }
        
        self.time_blocks = {
            'short': '15-30 min',
            'medium': '30-60 min',
            'long': '1-2 hours'
        }
    
    def generate_daily_plan(self, skill_gaps, user_progress, learning_pace='moderate', 
                           available_hours=2):
        """
        Generate a personalized daily learning plan
        
        Args:
            skill_gaps: List of skills to learn with priorities
            user_progress: Dict of current progress for each skill
            learning_pace: 'slow', 'moderate', or 'intensive'
            available_hours: Hours available per day
        
        Returns:
            List of learning tasks for today
        """
        tasks = []
        
        # Determine number of tasks based on pace
        if learning_pace == 'slow':
            num_tasks = 2
        elif learning_pace == 'moderate':
            num_tasks = 3
        else:  # intensive
            num_tasks = 4
        
        # Prioritize skills
        priority_skills = sorted(
            skill_gaps, 
            key=lambda x: (x.get('priority', 50), -user_progress.get(x['skill'], 0))
        )[:num_tasks]
        
        # Generate tasks for each skill
        for i, skill_gap in enumerate(priority_skills):
            skill = skill_gap['skill']
            current_progress = user_progress.get(skill, 0)
            
            # Determine activity type based on progress
            if current_progress < 20:
                activity_type = random.choice(['video', 'reading'])
            elif current_progress < 50:
                activity_type = random.choice(['reading', 'practice'])
            elif current_progress < 80:
                activity_type = 'practice'
            else:
                activity_type = random.choice(['project', 'review'])
            
            # Determine duration
            if i == 0:  # First task gets more time
                duration = self.time_blocks['long']
            elif i < num_tasks - 1:
                duration = self.time_blocks['medium']
            else:
                duration = self.time_blocks['short']
            
            task = {
                'skill': skill,
                'activity': random.choice(self.activity_types[activity_type]),
                'activity_type': activity_type,
                'duration': duration,
                'priority': skill_gap.get('priority', 50),
                'resources': skill_gap.get('resources', [])[:2],  # Top 2 resources
                'milestone': self._get_milestone(current_progress)
            }
            
            tasks.append(task)
        
        # Add motivation
        motivation_task = {
            'skill': 'Motivation',
            'activity': 'Read success story or watch motivational content',
            'activity_type': 'motivation',
            'duration': '5-10 min',
            'priority': 100,
            'resources': [],
            'milestone': 'Stay motivated!'
        }
        tasks.append(motivation_task)
        
        return tasks
    
    def _get_milestone(self, progress):
        """Get milestone description based on progress"""
        if progress < 20:
            return "Getting Started"
        elif progress < 40:
            return "Building Foundation"
        elif progress < 60:
            return "Developing Skills"
        elif progress < 80:
            return "Advanced Practice"
        else:
            return "Mastery & Projects"
    
    def generate_weekly_overview(self, skill_gaps, user_progress):
        """
        Generate a weekly learning overview
        """
        weekly_plan = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Distribute skills across the week
        num_skills = min(len(skill_gaps), 5)  # Focus on top 5 skills
        
        for i, day in enumerate(days[:5]):  # Weekdays
            skill_index = i % num_skills
            if skill_index < len(skill_gaps):
                skill = skill_gaps[skill_index]['skill']
                weekly_plan[day] = {
                    'focus_skill': skill,
                    'activities': ['Study', 'Practice', 'Review'],
                    'duration': '2 hours'
                }
        
        # Weekend - project work or review
        weekly_plan['Saturday'] = {
            'focus_skill': 'Project Work',
            'activities': ['Build portfolio project', 'Apply learned skills'],
            'duration': '3-4 hours'
        }
        
        weekly_plan['Sunday'] = {
            'focus_skill': 'Review & Rest',
            'activities': ['Review week progress', 'Plan next week', 'Rest'],
            'duration': '1-2 hours'
        }
        
        return weekly_plan
    
    def get_study_tips(self, learning_style='visual'):
        """
        Get personalized study tips based on learning style
        """
        tips = {
            'visual': [
                "📺 Watch video tutorials and animated explanations",
                "🎨 Create mind maps and diagrams",
                "📊 Use flowcharts to understand processes",
                "🖼️ Take screenshots and annotate them",
                "📝 Use color coding in notes"
            ],
            'auditory': [
                "🎧 Listen to podcasts and audiobooks",
                "🗣️ Explain concepts out loud",
                "👥 Join study groups and discussions",
                "🎤 Record yourself explaining topics",
                "🎵 Use mnemonic devices and rhymes"
            ],
            'kinesthetic': [
                "💻 Learn by doing - code along with tutorials",
                "🔨 Build projects immediately after learning",
                "🚶 Take breaks and move while studying",
                "✍️ Write code by hand first",
                "🎯 Practice with real-world scenarios"
            ],
            'reading': [
                "📚 Read documentation thoroughly",
                "📝 Take detailed notes",
                "📖 Follow structured textbooks",
                "✍️ Write summaries of what you learn",
                "📄 Keep a learning journal"
            ]
        }
        
        return tips.get(learning_style, tips['visual'])
    
    def calculate_estimated_completion(self, skill_gaps, available_hours_per_day=2):
        """
        Estimate when the user will complete their learning goals
        """
        total_hours = sum(gap.get('hours_needed', 20) for gap in skill_gaps)
        days_needed = int(total_hours / available_hours_per_day)
        
        completion_date = datetime.now() + timedelta(days=days_needed)
        
        return {
            'total_hours': total_hours,
            'days_needed': days_needed,
            'weeks_needed': int(days_needed / 7),
            'completion_date': completion_date.strftime('%B %d, %Y'),
            'hours_per_day': available_hours_per_day
        }
    
    def get_progress_summary(self, user_progress, skill_gaps):
        """
        Generate a summary of learning progress
        """
        total_skills = len(skill_gaps)
        
        if not total_skills:
            return {
                'completed_skills': 0,
                'in_progress_skills': 0,
                'not_started_skills': 0,
                'average_progress': 0
            }
        
        completed = sum(1 for skill in skill_gaps 
                       if user_progress.get(skill['skill'], 0) >= 80)
        in_progress = sum(1 for skill in skill_gaps 
                         if 20 <= user_progress.get(skill['skill'], 0) < 80)
        not_started = sum(1 for skill in skill_gaps 
                         if user_progress.get(skill['skill'], 0) < 20)
        
        avg_progress = sum(user_progress.get(skill['skill'], 0) 
                          for skill in skill_gaps) / total_skills
        
        return {
            'total_skills': total_skills,
            'completed_skills': completed,
            'in_progress_skills': in_progress,
            'not_started_skills': not_started,
            'average_progress': round(avg_progress, 1)
        }
    
    def get_achievement_badges(self, user_progress, total_days_learning):
        """
        Generate achievement badges based on progress
        """
        badges = []
        
        # Consistency badges
        if total_days_learning >= 7:
            badges.append("🔥 Week Warrior - 7 days streak")
        if total_days_learning >= 30:
            badges.append("💪 Month Master - 30 days streak")
        if total_days_learning >= 100:
            badges.append("🏆 Centurion - 100 days streak")
        
        # Skill mastery badges
        mastered_skills = sum(1 for progress in user_progress.values() if progress >= 80)
        if mastered_skills >= 1:
            badges.append("⭐ First Skill Mastered")
        if mastered_skills >= 5:
            badges.append("🌟 Skill Collector - 5 skills mastered")
        if mastered_skills >= 10:
            badges.append("💫 Expert - 10 skills mastered")
        
        # Progress badges
        avg_progress = sum(user_progress.values()) / len(user_progress) if user_progress else 0
        if avg_progress >= 25:
            badges.append("🎯 Quarter Way There")
        if avg_progress >= 50:
            badges.append("🚀 Halfway Hero")
        if avg_progress >= 75:
            badges.append("🎓 Almost There!")
        
        return badges
