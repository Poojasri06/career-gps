"""
Email Template Generator
Creates professional email templates for job applications, cold emails, and networking
"""
from datetime import datetime

class EmailTemplateGenerator:
    
    def generate_application_email(self, job_title, company_name, user_name, 
                                   user_skills, user_experience=None):
        """
        Generate a professional job application email
        """
        skills_str = ", ".join(user_skills[:5])
        
        experience_section = ""
        if user_experience:
            experience_section = f"\n\nDuring my {user_experience}, I have developed strong expertise in {skills_str}, which aligns perfectly with the requirements for this position."
        
        template = f"""Subject: Application for {job_title} Position at {company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. As a passionate and motivated professional with expertise in {skills_str}, I am excited about the opportunity to contribute to your team.{experience_section}

What particularly draws me to {company_name} is your commitment to innovation and excellence in the industry. I am impressed by your recent projects and would be honored to bring my skills and enthusiasm to your organization.

Key strengths I can bring to this role:
• Strong technical skills in {user_skills[0] if user_skills else 'relevant technologies'}
• Proven ability to learn quickly and adapt to new challenges
• Excellent problem-solving and analytical capabilities
• Strong communication and team collaboration skills

I have attached my resume for your review. I would welcome the opportunity to discuss how my background, skills, and enthusiasm can contribute to {company_name}'s continued success.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{user_name}

---
[Attach your resume and include your contact information]
"""
        return template
    
    def generate_cold_email_networking(self, recipient_name, recipient_company, 
                                      user_name, user_background, common_interest):
        """
        Generate a cold email for networking purposes
        """
        template = f"""Subject: Connecting on {common_interest}

Hi {recipient_name},

I hope this message finds you well. My name is {user_name}, and I came across your profile while researching professionals at {recipient_company}.

I'm particularly impressed by your work in {common_interest}, and as someone who is {user_background}, I would greatly appreciate the opportunity to connect and learn from your experience.

I understand you're busy, but I would be grateful for any insights you might share about:
• Your journey in the industry
• Key skills that have been most valuable in your career
• Any advice for someone looking to grow in this field

Would you be open to a brief 15-20 minute virtual coffee chat in the coming weeks? I'm flexible with timing and happy to work around your schedule.

Thank you for considering my request. I look forward to the possibility of connecting.

Best regards,
{user_name}

P.S. I'm also happy to share my background or anything that might be helpful for you in return.
"""
        return template
    
    def generate_cold_email_job_inquiry(self, company_name, department, 
                                       user_name, user_skills, career_goal):
        """
        Generate a cold email inquiring about job opportunities
        """
        skills_str = ", ".join(user_skills[:4])
        
        template = f"""Subject: Exploring Opportunities in {department} at {company_name}

Dear {company_name} Team,

I hope this email finds you well. My name is {user_name}, and I am reaching out to inquire about potential opportunities within your {department} team.

I am a motivated professional with strong skills in {skills_str}, and I am passionate about {career_goal}. {company_name}'s reputation for innovation and excellence makes it an ideal place for me to grow and contribute.

While I understand you may not have current openings, I wanted to:
• Introduce myself and express my interest in joining your team
• Share my enthusiasm for the work {company_name} is doing
• Ask if I could be considered for future opportunities

I have attached my resume for your reference. I would be delighted to discuss how my skills and passion could align with {company_name}'s needs, either now or in the future.

Thank you for taking the time to read my email. I appreciate any guidance or advice you might offer.

Best regards,
{user_name}

---
[Attach your resume and portfolio if applicable]
"""
        return template
    
    def generate_follow_up_email(self, interviewer_name, company_name, 
                                 position, user_name, interview_date):
        """
        Generate a follow-up thank you email after interview
        """
        template = f"""Subject: Thank You - {position} Interview

Dear {interviewer_name},

I wanted to take a moment to thank you for taking the time to speak with me about the {position} role at {company_name} on {interview_date}. I truly enjoyed our conversation and learning more about your team and the exciting projects you're working on.

Our discussion reinforced my enthusiasm for this opportunity. I am particularly excited about [mention specific aspect discussed during interview], and I am confident that my skills and passion would allow me to make valuable contributions to your team.

If you need any additional information from me, please don't hesitate to reach out. I am very excited about the possibility of joining {company_name} and contributing to your continued success.

Thank you again for your time and consideration. I look forward to hearing from you regarding the next steps.

Best regards,
{user_name}
"""
        return template
    
    def generate_linkedin_connection_message(self, recipient_name, common_ground):
        """
        Generate a LinkedIn connection request message
        """
        template = f"""Hi {recipient_name},

I came across your profile and was impressed by your experience in {common_ground}. I'm looking to connect with professionals in this field to learn and grow. Would you be open to connecting?

Looking forward to staying in touch!
"""
        return template
    
    def generate_referral_request_email(self, contact_name, company_name, 
                                       position, user_name, relationship):
        """
        Generate an email requesting a job referral
        """
        template = f"""Subject: Seeking Your Guidance - {position} at {company_name}

Hi {contact_name},

I hope you're doing well! I'm reaching out because I saw that {company_name} has an opening for a {position} role, and I immediately thought of you.

{relationship}, I've always valued your insights and advice. Given your experience at {company_name}, I would greatly appreciate any guidance you might offer about this opportunity.

I believe my skills and experience would be a strong fit for this role, and if you feel comfortable, I would be honored if you could provide a referral or introduce me to the hiring manager.

I've attached my resume for your reference. Even if a referral isn't possible, I would love to hear any advice you might have about the application process.

Thank you so much for considering my request. I truly appreciate your time and support.

Best regards,
{user_name}

---
[Attach your resume]
"""
        return template
    
    def generate_skills_showcase_email(self, recipient_name, user_name, 
                                      project_description, skills_used):
        """
        Generate an email showcasing your skills through a project
        """
        skills_str = ", ".join(skills_used)
        
        template = f"""Subject: Showcasing My Work in {skills_used[0] if skills_used else 'Technology'}

Hi {recipient_name},

My name is {user_name}, and I wanted to share a recent project I completed that demonstrates my capabilities in {skills_str}.

Project Overview:
{project_description}

I created this project to solve [problem] and implemented features such as [key features]. The experience strengthened my skills in {skills_str} and taught me valuable lessons about [key learning].

I would love to hear your feedback on this project, and I'm also very interested in learning about opportunities where I could apply these skills professionally.

You can view the project here: [project link]
GitHub repository: [github link]

Thank you for taking the time to review my work. I look forward to any insights you might share.

Best regards,
{user_name}
"""
        return template
    
    def get_email_tips(self, email_type):
        """
        Get tips for writing effective emails
        """
        tips = {
            'application': [
                "✅ Keep it concise - aim for 3-4 short paragraphs",
                "✅ Customize for each company - mention specific details",
                "✅ Show enthusiasm but remain professional",
                "✅ Highlight 2-3 key relevant skills or achievements",
                "✅ Include a clear call-to-action",
                "✅ Proofread carefully for errors",
                "✅ Use a professional email address"
            ],
            'cold_email': [
                "✅ Research the recipient before reaching out",
                "✅ Keep the first email brief (under 200 words)",
                "✅ Be specific about why you're reaching out",
                "✅ Show you've done your homework about their work",
                "✅ Don't ask for too much in the first email",
                "✅ Make it easy for them to respond",
                "✅ Follow up if no response after 1 week"
            ],
            'follow_up': [
                "✅ Send within 24 hours of the interview",
                "✅ Mention something specific from your conversation",
                "✅ Reiterate your interest in the position",
                "✅ Keep it brief and appreciative",
                "✅ Proofread the interviewer's name and title",
                "✅ Don't ask about the decision timeline unless appropriate"
            ],
            'networking': [
                "✅ Be genuine and authentic in your approach",
                "✅ Offer value, not just requests",
                "✅ Respect their time - keep initial messages brief",
                "✅ Find common ground or mutual connections",
                "✅ Be patient - not everyone will respond",
                "✅ Maintain relationships even after getting help"
            ]
        }
        
        return tips.get(email_type, tips['application'])
