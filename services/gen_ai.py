from typing import Dict, Any, List
from services.llm import LLMClient

llm = LLMClient()


def generate_explanation_for_score(score_data: Dict[str, Any], gap_analysis: Dict[str, Any]) -> str:
    """Enhance the readiness explanation using an LLM when available."""
    # Build concise context
    top_priority = gap_analysis.get('priority_skills', [])[:5]
    missing = gap_analysis.get('missing_skills', [])[:8]
    breakdown = score_data.get('breakdown', {})

    prompt = (
        "You are a helpful career coach. The user has a readiness score with the following breakdown: "
        f"{breakdown}. The top priority skills: {top_priority}. The missing skills: {missing}. "
        "Provide a short explanation (1-3 sentences) why this score is at this level and 3 practical next steps the user can take, concise and actionable."
    )

    return llm.generate_text(prompt, max_tokens=250)


def generate_learning_plan(gap_analysis: Dict[str, Any]) -> str:
    """Produce a short learning plan (phases + weekly estimate) for given gap analysis."""
    priority = gap_analysis.get('priority_skills', [])[:6]
    estimated_weeks = gap_analysis.get('estimated_learning_time_weeks')

    prompt = (
        "Given the following priority skills: " + ", ".join(priority) + ". "
        f"Estimated total weeks: {estimated_weeks}. "
        "Return a 3-phase learning plan with phase names, duration (weeks), and 2 concrete activities per phase. Keep it short and in bullet form."
    )

    return llm.generate_text(prompt, max_tokens=400)


def answer_chat(prompt: str, skills: List[str] = None, career: Dict[str, Any] = None, gap_analysis: Dict[str, Any] = None) -> str:
    """General chat wrapper that uses the LLM to produce a friendly answer.
    It injects small amounts of context when available.
    """
    ctx = []
    if skills:
        ctx.append(f"User skills: {', '.join(skills)}")
    if career:
        ctx.append(f"Target career: {career.get('role_name')}")
    if gap_analysis:
        ctx.append(f"Priority skills: {', '.join(gap_analysis.get('priority_skills', [])[:5])}")

    prompt_full = "\n\n".join(["You are an expert career coach.", "\n".join(ctx), prompt])
    return llm.generate_text(prompt_full, max_tokens=300)
