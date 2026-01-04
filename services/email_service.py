"""
Email Notification Service
Sends daily updates, learning plans, and motivational content to users
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random

class EmailService:
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
    
    def configure(self, sender_email, sender_password):
        """Configure email credentials"""
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def _get_motivational_quote(self):
        """Get a random motivational quote"""
        quotes = [
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "Believe you can and you're halfway there. - Theodore Roosevelt",
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Your limitation—it's only your imagination.",
            "Push yourself, because no one else is going to do it for you.",
            "Great things never come from comfort zones.",
            "Dream it. Wish it. Do it.",
            "Success doesn't just find you. You have to go out and get it.",
            "The harder you work for something, the greater you'll feel when you achieve it.",
            "Dream bigger. Do bigger.",
            "Don't stop when you're tired. Stop when you're done.",
            "Wake up with determination. Go to bed with satisfaction.",
            "Do something today that your future self will thank you for.",
            "Little things make big days.",
            "It's going to be hard, but hard does not mean impossible.",
            "Don't wait for opportunity. Create it.",
            "Sometimes we're tested not to show our weaknesses, but to discover our strengths.",
            "The key to success is to focus on goals, not obstacles.",
            "Dream it. Believe it. Build it."
        ]
        return random.choice(quotes)
    
    def _generate_email_html(self, user_name, results, today_plan, job_info=None):
        """Generate HTML email content"""
        quote = self._get_motivational_quote()
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Build job section if provided
        job_section = ""
        if job_info:
            job_section = f"""
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #0066cc;">🎯 Job Opportunities for You</h2>
                {job_info}
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section {{
                    margin: 25px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }}
                .motivation {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-style: italic;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
                h2 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                ul {{
                    padding-left: 20px;
                }}
                .metric {{
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                    padding: 10px 15px;
                    background-color: #e8f4f8;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Career GPS Daily Update</h1>
                    <p>{current_date}</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name}! 👋</h2>
                    <p>Here's your daily career progress update and learning plan.</p>
                    
                    <div class="section">
                        <h2>📊 Your Progress So Far</h2>
                        {results}
                    </div>
                    
                    <div class="section">
                        <h2>📚 Today's Learning Plan</h2>
                        {today_plan}
                    </div>
                    
                    {job_section}
                    
                    <div class="motivation">
                        <h3>💪 Daily Motivation</h3>
                        <p style="font-size: 1.1em;">{quote}</p>
                    </div>
                    
                    <div class="footer">
                        <p>Keep up the great work! 🚀</p>
                        <p style="font-size: 0.9em;">You're making progress every day towards your career goals.</p>
                        <p style="font-size: 0.8em; color: #999;">
                            Sent by Career GPS - Your AI Career Mentor<br>
                            To update your notification preferences, log in to your account.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_daily_update(self, recipient_email, user_name, results, today_plan, job_info=None):
        """
        Send daily update email
        Returns: (success: bool, message: str)
        """
        if not self.sender_email or not self.sender_password:
            return False, "Email service not configured"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 Your Daily Career Update - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Generate HTML content
            html_content = self._generate_email_html(user_name, results, today_plan, job_info)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
        
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def format_results(self, readiness_score, skills_mastered, skills_in_progress):
        """Format results for email"""
        html = f"""
        <div class="metric">
            <strong>Readiness Score:</strong> {readiness_score}%
        </div>
        <div class="metric">
            <strong>Skills Mastered:</strong> {skills_mastered}
        </div>
        <div class="metric">
            <strong>Skills In Progress:</strong> {skills_in_progress}
        </div>
        """
        return html
    
    def format_learning_plan(self, tasks):
        """Format learning plan for email"""
        if not tasks:
            return "<p>No tasks scheduled for today. Take a break or review what you've learned!</p>"
        
        html = "<ul>"
        for task in tasks:
            html += f"<li><strong>{task['skill']}</strong>: {task['activity']} ({task['duration']})</li>"
        html += "</ul>"
        return html
    
    def format_job_opportunities(self, jobs):
        """Format job opportunities for email"""
        if not jobs:
            return ""
        
        html = "<ul>"
        for job in jobs[:5]:  # Limit to 5 jobs
            html += f"""
            <li>
                <strong>{job['title']}</strong> at {job['company']}<br>
                <span style="color: #666;">{job['location']} | {job['type']}</span><br>
                <a href="{job['url']}" style="color: #0066cc;">View Job</a>
            </li>
            <br>
            """
        html += "</ul>"
        return html
