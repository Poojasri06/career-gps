from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from utils.helpers import load_data
from services.skill_extractor import SkillExtractor
from services.career_matcher import CareerMatcher
from services.skill_gap import SkillGapAnalyzer
from services.readiness_score import ReadinessScoreCalculator
from services.simulator import CareerSimulator
from services.gen_ai import generate_explanation_for_score, generate_learning_plan, answer_chat

app = FastAPI(title="Career GPS API")

# Load data and init services at startup
careers_df, skills_df, resources_df = load_data()
skill_extractor = SkillExtractor(skills_df)
career_matcher = CareerMatcher(careers_df)
gap_analyzer = SkillGapAnalyzer(skills_df)
readiness_calc = ReadinessScoreCalculator()
simulator = CareerSimulator(skills_df)


class ReadinessRequest(BaseModel):
    skills: List[str]
    career: Optional[Dict[str, Any]] = None


class SimulateRequest(BaseModel):
    skills: List[str]
    career: Dict[str, Any]
    new_skills: List[str]


class ChatRequest(BaseModel):
    prompt: str
    skills: Optional[List[str]] = None
    career: Optional[Dict[str, Any]] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/readiness")
def readiness(req: ReadinessRequest):
    try:
        career = req.career
        if not career:
            # pick top match
            matches = career_matcher.match_careers(req.skills, '', top_n=1)
            if not matches:
                raise HTTPException(status_code=400, detail="No career matches found")
            career = matches[0]

        gap = gap_analyzer.analyze_gap(req.skills, career)
        score = readiness_calc.calculate_score(gap)
        # enhance explanation using Gen-AI when available
        try:
            enhanced = generate_explanation_for_score(score, gap)
            if enhanced:
                score['explanation'] = enhanced
        except Exception:
            pass
        return {"gap_analysis": gap, "readiness": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate/learn")
def simulate_learn(req: SimulateRequest):
    try:
        career = req.career
        # If the provided career dict doesn't include required skill details, attempt to resolve a full career match
        if not career or 'required_skills' not in career:
            matches = career_matcher.match_careers(req.skills, '', top_n=5)
            # If caller provided a role_name, try to find it
            if career and career.get('role_name'):
                chosen = next((m for m in matches if m.get('role_name') == career.get('role_name')), None)
                career = chosen or (matches[0] if matches else career)
            else:
                career = matches[0] if matches else career

        baseline = simulator.create_baseline(req.skills, career)
        result = simulator.simulate_add_skills(baseline, req.new_skills, career)
        return {"baseline": baseline, "simulation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(req: ChatRequest):
    prompt = req.prompt or ""
    lower = prompt.lower()

    # Prefer provided skills/career but allow fallback
    skills = req.skills or []
    career = req.career
    if not skills:
        # try to extract skills from prompt
        extracted = skill_extractor.extract_from_text(prompt)
        skills = extracted or []

    # If prompt asks about learning or what-if, route to simulate
    if 'learn' in lower or 'what if' in lower or 'if i learn' in lower:
        # attempt to parse skills mentioned after 'learn'
        candidate = None
        if 'learn' in lower:
            try:
                candidate = prompt.split('learn', 1)[1].strip(' :.?')
            except Exception:
                candidate = None
        if not candidate:
            candidate = prompt
        # fall back: use extractor on candidate
        new_skills = skill_extractor.extract_from_text(candidate) or [candidate]
        if not career:
            matches = career_matcher.match_careers(skills or new_skills, '', top_n=1)
            career = matches[0] if matches else None
        if not career:
            raise HTTPException(status_code=400, detail="No career context available for simulation")
        baseline = simulator.create_baseline(skills, career)
        sim = simulator.simulate_add_skills(baseline, new_skills, career)
        return {"type": "what_if_learn", "simulation": sim}

    # Otherwise attempt a generative answer or return readiness if possible
    if career:
        gap = gap_analyzer.analyze_gap(skills, career)
        score = readiness_calc.calculate_score(gap)
        # use gen-ai to answer the chat prompt enriched with context
        try:
            reply = answer_chat(prompt, skills, career, gap)
            return {"type": "chat", "reply": reply, "gap": gap, "readiness": score}
        except Exception:
            return {"type": "readiness", "gap": gap, "readiness": score}

    return {"type": "note", "message": "I can simulate learning or compute readiness. Provide skills and optionally a career."}
