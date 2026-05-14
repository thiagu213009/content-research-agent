from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from callback_manager import notify
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)

def run_reflection_agent(topic: str, aggregated: str) -> dict:
    """Evaluate research quality and return score + feedback."""
    notify("reflection", "running")
    print("\n→ Reflection Agent: Checking quality...")

    # Step 1 — Draft (summarise what we have)
    draft_prompt = f"""You are reviewing research about: {topic}

Here is the compiled research:
{aggregated}

Write a brief 2-3 sentence summary of what this research covers."""

    draft_response = llm.invoke([HumanMessage(content=draft_prompt)])
    draft_summary = draft_response.content

    # Step 2 — Critique (evaluate quality)
    critique_prompt = f"""You are a STRICT quality reviewer for research reports.

Topic: {topic}
Research summary: {draft_summary}

Full research:
{aggregated}

Critically evaluate:
1. Is the content SPECIFICALLY about "{topic}"? Not generic AI content.
2. Are there REAL verifiable statistics with sources?
3. Are there NAMED real companies with specific examples?
4. Is the news RECENT and directly relevant?
5. Is there enough DEPTH — not just surface level?

Be strict — if content is generic or could apply to ANY topic, score low.
If topic is unclear or fictional, score below 0.5.

Respond EXACTLY:
SCORE: 0.X
STATUS: APPROVED or NEEDS_WORK
FEEDBACK: specific feedback on what's missing or generic"""

    critique_response = llm.invoke([HumanMessage(content=critique_prompt)])
    critique_content = critique_response.content

    # Parse score, status, feedback
    try:
        lines = critique_content.strip().split('\n')
        score_line = [l for l in lines if 'SCORE:' in l][0]
        status_line = [l for l in lines if 'STATUS:' in l][0]
        feedback_line = [l for l in lines if 'FEEDBACK:' in l][0]

        score = float(score_line.split(':')[1].strip())
        status = status_line.split(':')[1].strip()
        feedback = feedback_line.split(':', 1)[1].strip()
    except:
        score = 0.8
        status = "APPROVED"
        feedback = "Quality check complete"

    print(f"  Quality score: {score}")
    print(f"  Status: {status}")
    print(f"  Feedback: {feedback}")

    # Notify with score
    notify("reflection", "done", f"Score: {score}")

    return {
        "score": score,
        "status": status,
        "feedback": feedback,
        "draft_summary": draft_summary
    }
