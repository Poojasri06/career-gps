# 🎯 Career GPS - AI Career Readiness Mentor

**A real-time AI Career GPS that doesn't just guide students—it reroutes them toward success.**

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Overview

Career GPS is an AI-powered career readiness mentor designed for students and early professionals. Unlike static career recommendation platforms, Career GPS continuously evaluates skills, learning behavior, and goals to simulate multiple career paths and dynamically reroute recommendations in real time.

## 🚀 Core Differentiator

### **What-If Career Simulation Engine**

The standout feature that sets Career GPS apart:

- **Switch domains** - See how your readiness changes for different careers
- **Skip certifications** - Understand the impact of avoiding formal credentials
- **Focus on projects** - Simulate hands-on learning vs traditional education
- **Pause learning** - Visualize the effect of taking breaks on career timelines
- **Add new skills** - Test how specific skills improve your readiness

All simulations recalculate in real-time:
- ✅ Skill gaps
- ⏱️ Time to readiness
- ⚠️ Risk level
- 📊 Readiness score

## 🎯 Key Features

### 1. **Intelligent Career Matching**
- AI-powered matching using TF-IDF embeddings
- Matches user skills with 15+ career paths
- Provides match confidence scores and skill overlap analysis

### 2. **Comprehensive Skill Gap Analysis**
- Identifies known, partial, and missing skills
- Calculates weighted importance of each skill
- Provides priority learning recommendations

### 3. **Dynamic Career Readiness Score**
- Multi-dimensional scoring (0-100 scale)
- Components:
  - Skill coverage (50%)
  - Skill importance (25%)
  - Skill depth (15%)
  - Learning consistency (10%)
- Updates dynamically with simulations

### 4. **Adaptive Learning Roadmap**
- Personalized weekly learning plans
- Considers prerequisites and skill dependencies
- Recommends courses, projects, and resources
- Estimates realistic timelines

### 5. **Interactive Visualizations**
- Plotly-powered charts and graphs
- Career comparison dashboards
- Skill gap breakdowns
- Simulation impact visualizations

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Rapid UI development
- **Plotly** - Interactive visualizations
- **Matplotlib** - Additional charts

### Backend / Core Logic
- **Python 3.8+**
- Modular architecture (services/, models/, utils/)

### AI / ML
- **Scikit-learn** - ML models and TF-IDF vectorization
- **NLP** - Text processing with TF-IDF and sentence embeddings
- **Hybrid approach** - Rule-based + ML for reliability

### Data
- **Pandas** - Data manipulation
- **CSV/JSON** - Structured datasets for careers, skills, and resources

## 📁 Project Structure

```
career_gps/
│
├── app.py                      # Main Streamlit application
│
├── data/
│   ├── careers.csv            # 15 career roles with requirements
│   ├── skills.csv             # 90+ skills with metadata
│   └── resources.csv          # 30+ learning resources
│
├── services/
│   ├── skill_extractor.py     # Extracts skills from user input
│   ├── career_matcher.py      # Matches users to careers
│   ├── skill_gap.py           # Analyzes skill gaps
│   ├── simulator.py           # What-If simulation engine
│   └── readiness_score.py     # Career readiness calculator
│
├── utils/
│   ├── embeddings.py          # TF-IDF embeddings and similarity
│   └── helpers.py             # Utility functions
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**
```bash
cd career_gps
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open your browser**
```
The app will automatically open at http://localhost:8501
```

## 📖 How to Use

### Step 1: Create Your Profile
- Enter your name, education, and experience level
- List your current skills (comma-separated or free text)
- Optionally add interests and career goals

### Step 2: Discover Career Matches
- View your top 5 career matches
- See match scores, salary info, and growth rates
- Compare skill overlaps across careers

### Step 3: Analyze Skill Gaps
- Select a career to analyze
- View your Career Readiness Score (0-100)
- See exactly which skills you need to learn
- Get priority skill recommendations

### Step 4: Run What-If Simulations
- **Switch Career**: See readiness for alternative paths
- **Skip Certifications**: Understand certification importance
- **Focus on Projects**: Compare project-based vs traditional learning
- **Pause Learning**: Visualize impact of breaks
- **Add Skills**: Test how new skills improve readiness

### Step 5: Get Your Roadmap
- Receive a phase-by-phase learning plan
- Access curated resources for each skill
- Download your roadmap as JSON

## 🎓 Target Users

- **College students** exploring career options
- **Final-year students** preparing for job market
- **Fresh graduates** planning career transitions
- **Career switchers** evaluating new paths

## 📊 Sample Careers Included

- Full Stack Developer
- Data Scientist
- Machine Learning Engineer
- Frontend Developer
- Backend Developer
- DevOps Engineer
- Mobile App Developer
- Cloud Architect
- Product Manager
- UI/UX Designer
- Data Analyst
- Cybersecurity Analyst
- QA Engineer
- Business Analyst
- AI Research Scientist

## 🧪 Example Use Cases

### Use Case 1: College Student Exploring Options
*"I know Python and JavaScript. Which career path is best for me?"*
- Create profile with Python, JavaScript
- View matched careers (Full Stack, Data Scientist, etc.)
- Compare readiness scores across careers
- Simulate switching between paths

### Use Case 2: Career Switcher
*"I'm a developer wanting to move into data science. What's the gap?"*
- Input current development skills
- Analyze Data Scientist career
- See missing skills (ML, Statistics, etc.)
- Get 16-week learning roadmap

### Use Case 3: Decision Validation
*"Should I get AWS certification or focus on projects?"*
- Run "Skip Certifications" simulation
- Run "Focus on Projects" simulation
- Compare readiness scores and timelines
- Make data-driven decision

## 🎯 Hackathon Success Criteria Met

✅ **Clear Differentiation** - What-If Simulation Engine is unique  
✅ **Explainable AI** - All scores and recommendations are transparent  
✅ **Demo Ready** - Fully functional Streamlit app  
✅ **Scalable Concept** - Modular architecture for easy expansion  
✅ **Problem-Solution Fit** - Addresses real pain points

## 🔮 Future Enhancements

### Phase 2 (Post-Hackathon)
- [ ] FastAPI backend for API separation
- [ ] SQLite database for user persistence
- [ ] User authentication and progress tracking
- [ ] Real-time job market data integration
- [ ] Community features (mentorship, peer learning)

### Phase 3 (Production)
- [ ] LLM integration (GPT-4, Claude) for personalized advice
- [ ] LinkedIn profile analysis
- [ ] Resume builder and optimization
- [ ] Interview preparation based on career path
- [ ] Company-specific skill matching

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Development

### Adding New Careers
Edit `data/careers.csv` with the following columns:
- role_id, role_name, category, description
- required_skills, importance_weights
- avg_salary, growth_rate

### Adding New Skills
Edit `data/skills.csv` with:
- skill_id, skill_name, category, difficulty
- learning_time_weeks, prerequisites

### Adding Learning Resources
Edit `data/resources.csv` with:
- resource_id, skill_name, resource_type
- resource_name, url, duration_weeks, difficulty

## 🐛 Troubleshooting

### Issue: Module not found
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Port already in use
```bash
streamlit run app.py --server.port 8502
```

### Issue: Data files not loading
Ensure you're running from the `career_gps/` directory and `data/` folder exists.

## 📧 Contact

For questions, feedback, or collaboration:
- Open an issue on GitHub
- Reach out during the hackathon demo

---

## 🎉 Vision Statement

**"A real-time AI Career GPS that doesn't just guide students—it reroutes them toward success."**

Career GPS empowers students and professionals to make informed, data-driven career decisions. By simulating real-world scenarios and providing adaptive guidance, we're transforming career planning from static recommendations to dynamic, personalized mentorship.

---

**Built with ❤️ for hackathon success and real-world impact.**
