# Career GPS - Detailed Project Description

## 1) Project Summary

Career GPS is an AI-assisted career planning and readiness platform designed for students, fresh graduates, and early-career professionals. Instead of giving one-time static recommendations, it continuously evaluates a user's current skill profile, career goals, and learning actions to provide practical, explainable guidance.

The platform combines deterministic logic (rule-based scoring and simulation) with optional Gen-AI enhancement (LLM-generated explanations and learning guidance). This hybrid design keeps outputs reliable, debuggable, and useful even when an external LLM is unavailable.

In short, Career GPS acts like a navigation system for careers: it estimates your current position, identifies the gap to your destination role, and recalculates route options when your constraints or goals change.

## 2) Problem It Solves

Many learners struggle with three common problems:

1. They do not know which career path best fits their current skills.
2. They cannot clearly see what skills are missing for a target role.
3. They are unsure how specific choices (for example, skipping certifications or focusing on projects) affect readiness and timeline.

Career GPS addresses these issues by turning vague career advice into measurable outputs: match scores, skill gaps, readiness percentages, simulation deltas, and actionable learning plans.

## 3) Product Vision

Career GPS aims to become a full Gen-AI career platform where users can:

1. Discover role matches from their existing skill set.
2. Understand readiness in transparent, explainable terms.
3. Run what-if simulations before committing time and effort.
4. Receive adaptive daily and weekly learning guidance.
5. Access practical execution tools (job search, application emails, networking templates).

## 4) Core Capabilities

### A. Intelligent Career Matching

- Maps user skills to career roles using lightweight NLP/ML and matching logic.
- Produces ranked role suggestions based on overlap and relevance.
- Helps users compare realistic near-term and stretch opportunities.

### B. Skill Extraction and Normalization

- Converts free-text input (resume text, skill lists, profile notes) into normalized skill tokens.
- Improves consistency for downstream analysis, scoring, and simulation.

### C. Skill Gap Analysis

- For a chosen target role, separates skills into:
  - matched skills (already strong)
  - partial skills (present but weak)
  - missing skills (critical gaps)
- Enables priority-driven upskilling instead of random course consumption.

### D. Readiness Scoring (0-100)

- Generates a quantitative readiness score for a selected career path.
- Includes explainable components and next-step guidance.
- Returns user-friendly output with improvement direction, not just a number.

### E. What-If Simulation Engine

- Simulates how readiness changes when the user makes a decision.
- Example scenarios:
  - add a new skill
  - switch target career
  - prioritize project-first learning
  - skip certain credentials
  - estimate impact of planned learning
- Produces compact summaries for faster decision-making.

### F. Gen-AI Enhancements (Optional)

- Uses an LLM wrapper to generate richer explanations and concise plans.
- Falls back to deterministic outputs when API keys or providers are unavailable.
- Keeps the platform functional in offline or low-cost environments.

### G. User-Focused Productivity Features

- Account-based access with local private profile persistence.
- Daily plan generation and progress-oriented learning structure.
- Job search support for entry-level and early-career applications.
- Email template generation for applications, networking, follow-up, and referrals.
- Daily email notification capability for consistency and motivation.

## 5) Architecture and Codebase Design

The codebase is organized in a modular service-oriented layout to separate concerns and support easy iteration.

- `services/`
  - `career_matcher.py`: role matching logic
  - `skill_extractor.py`: text-to-skill processing
  - `skill_gap.py`: gap segmentation and prioritization
  - `readiness_score.py`: score calculation plus explanation payload
  - `simulator.py`: scenario simulation and summary generation
  - `gen_ai.py`, `llm.py`: optional LLM orchestration
  - `daily_learning.py`, `job_search.py`, `email_service.py`, `email_templates.py`, `user_auth.py`: user productivity and engagement services

- `utils/`
  - `embeddings.py`, `helpers.py`: utility methods, reusable transforms, and estimation helpers

- Application layers
  - `app.py`: Streamlit user interface and optional CLI mode
  - `app_api.py`: FastAPI endpoints for integration and backend use

- `data/`
  - `careers.csv`, `skills.csv`, `resources.csv`, `users.json`: local data sources and persisted user state

This structure supports incremental upgrades (for example replacing one service with a stronger model) without rewriting the entire app.

## 6) API and Integration Readiness

Career GPS already exposes backend endpoints suitable for web clients, automation, or third-party integrations.

Current API coverage includes:

- `/readiness`
- `/simulate/learn`
- `/chat`

This makes the project suitable for evolution from a demo app into a platform service.

## 7) User Experience Flow

Typical user journey:

1. User enters current skills and profile context.
2. System extracts and normalizes skill evidence.
3. Career matcher returns role options.
4. User chooses a target role for deep analysis.
5. Skill-gap and readiness services generate current-state diagnostics.
6. User runs one or more simulations to compare strategic choices.
7. System returns updated scores, summaries, and next learning actions.
8. User tracks progress daily and optionally uses job and communication tools.

## 8) Why This Approach Works

Career GPS balances practicality and intelligence by combining:

1. Transparent rule-based logic for trust and explainability.
2. Optional Gen-AI text generation for richer coaching-style output.
3. Simulation-first interaction for decision support, not passive advice.
4. End-to-end workflow support from assessment to execution.

The result is a product that is useful both as a technical prototype and as a deployable foundation for a larger career-tech platform.

## 9) Current Maturity

The project is currently at a strong prototype/early platform stage:

- Functional UI and API
- Modular service design
- Explainable readiness and gap logic
- Simulation engine in place
- Productivity features beyond pure scoring

This maturity level is ideal for hackathons, demos, pilot deployments, and iterative product expansion.

## 10) Recommended Next Phase

To evolve into a production-grade Gen-AI platform, the most valuable next upgrades are:

1. Persistent database storage (profiles, history, simulation runs).
2. Vector search for semantic matching and retrieval.
3. Stronger auth/session management and secure config handling.
4. Expanded API surface (`/roadmap`, `/recommendations`, `/daily-plan`, webhook triggers).
5. Monitoring, evaluation metrics, and prompt/version governance for AI outputs.
6. Packaging an SDK for easier external integration.

## 11) Positioning Statement

Career GPS is a decision-intelligence platform for career growth. It helps users answer not only "What role fits me now?" but also "What should I do next, and what happens if I choose path A vs path B?".

By unifying matching, readiness analytics, simulation, and execution tools in one system, it transforms career planning from a static recommendation into a dynamic and actionable process.
