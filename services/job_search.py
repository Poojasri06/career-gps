"""
Job Search and Vacancy Service
Helps fresh graduates find relevant job opportunities
"""
import pandas as pd
from datetime import datetime
import random

class JobSearchService:
    def __init__(self, careers_df):
        self.careers_df = careers_df
        # Sample job boards and companies (in real app, integrate with APIs)
        self.job_boards = [
            'LinkedIn', 'Indeed', 'Glassdoor', 'AngelList', 
            'Monster', 'CareerBuilder', 'SimplyHired'
        ]
        
        self.sample_companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta',
            'Netflix', 'Tesla', 'Airbnb', 'Uber', 'Stripe',
            'Shopify', 'Spotify', 'Adobe', 'IBM', 'Oracle',
            'Salesforce', 'Twitter', 'Intel', 'NVIDIA', 'PayPal'
        ]
    
    def search_jobs(self, career_role, location='Remote', experience_level='entry'):
        """
        Search for job opportunities
        In production, integrate with real job APIs (LinkedIn, Indeed, etc.)
        Returns: List of job opportunities
        """
        # Get required skills for the career
        career_data = self.careers_df[
            self.careers_df['role_name'] == career_role
        ]
        
        if career_data.empty:
            return []
        
        # Generate sample job listings (in production, fetch from real APIs)
        jobs = []
        num_jobs = random.randint(5, 15)
        
        for i in range(num_jobs):
            job = {
                'id': f'job_{i}_{datetime.now().timestamp()}',
                'title': career_role if random.random() > 0.3 else f"Junior {career_role}",
                'company': random.choice(self.sample_companies),
                'location': location if random.random() > 0.5 else random.choice(['Remote', 'Hybrid', 'On-site']),
                'type': random.choice(['Full-time', 'Contract', 'Part-time', 'Internship']),
                'experience': experience_level,
                'salary_range': self._generate_salary_range(experience_level),
                'posted_date': self._generate_posted_date(),
                'url': f'https://linkedin.com/jobs/{i}',  # Placeholder
                'description': f"Exciting opportunity for {career_role}. We're looking for passionate individuals to join our team.",
                'requirements': career_data.iloc[0]['required_skills'].split(',')[:5] if 'required_skills' in career_data.columns else [],
                'source': random.choice(self.job_boards)
            }
            jobs.append(job)
        
        return jobs
    
    def _generate_salary_range(self, experience_level):
        """Generate salary range based on experience level"""
        if experience_level == 'entry':
            min_sal = random.randint(50, 70)
            max_sal = min_sal + random.randint(15, 25)
        elif experience_level == 'mid':
            min_sal = random.randint(70, 100)
            max_sal = min_sal + random.randint(20, 40)
        else:
            min_sal = random.randint(100, 150)
            max_sal = min_sal + random.randint(30, 50)
        
        return f"${min_sal}K - ${max_sal}K"
    
    def _generate_posted_date(self):
        """Generate random posted date"""
        days_ago = random.randint(1, 30)
        if days_ago == 1:
            return "1 day ago"
        elif days_ago < 7:
            return f"{days_ago} days ago"
        elif days_ago < 14:
            return "1 week ago"
        elif days_ago < 21:
            return "2 weeks ago"
        else:
            return f"{days_ago // 7} weeks ago"
    
    def get_job_match_score(self, job, user_skills):
        """
        Calculate how well a job matches user's skills
        Returns: Match score (0-100)
        """
        if not job['requirements']:
            return 50  # Default if no requirements specified
        
        # Convert user skills to lowercase for comparison
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        # Count matching skills
        matching = sum(1 for req in job['requirements'] 
                      if any(req.lower() in skill or skill in req.lower() 
                            for skill in user_skills_lower))
        
        total_requirements = len(job['requirements'])
        
        if total_requirements == 0:
            return 50
        
        match_score = int((matching / total_requirements) * 100)
        return match_score
    
    def get_recommended_jobs(self, career_role, user_skills, location='Remote', top_n=10):
        """
        Get recommended jobs sorted by match score
        """
        jobs = self.search_jobs(career_role, location)
        
        # Calculate match scores
        for job in jobs:
            job['match_score'] = self.get_job_match_score(job, user_skills)
        
        # Sort by match score
        jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jobs[:top_n]
    
    def get_job_application_tips(self, job, user_skills):
        """
        Get personalized tips for applying to a specific job
        """
        missing_skills = [req for req in job['requirements'] 
                         if not any(req.lower() in skill.lower() or skill.lower() in req.lower() 
                                   for skill in user_skills)]
        
        tips = []
        
        # Tip 1: Highlight matching skills
        if job['match_score'] > 70:
            tips.append("✅ Strong match! Emphasize your relevant skills in your application.")
        elif job['match_score'] > 50:
            tips.append("⚠️ Good match, but highlight how your skills transfer to the requirements.")
        else:
            tips.append("📚 Consider upskilling before applying to increase your chances.")
        
        # Tip 2: Missing skills
        if missing_skills:
            tips.append(f"🎯 Skills to highlight or learn: {', '.join(missing_skills[:3])}")
        
        # Tip 3: Experience level
        if job['experience'] == 'entry':
            tips.append("👶 Entry-level position - perfect for fresh graduates!")
        
        # Tip 4: Company research
        tips.append(f"🔍 Research {job['company']}'s culture and recent projects before applying.")
        
        # Tip 5: Application timing
        if 'day' in job['posted_date'] or '1 week' in job['posted_date']:
            tips.append("⏰ Recently posted! Apply soon to increase visibility.")
        
        return tips
