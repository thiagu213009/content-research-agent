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

def run_writer_agent(topic: str, aggregated: str, feedback: str = "") -> str:
    """Write final research report."""
    notify("writer", "running")
    print("\n→ Writer Agent: Writing final report...")

    feedback_section = ""
    if feedback:
        feedback_section = f"\nIncorporate this feedback: {feedback}"

    prompt = f"""Write a professional research report on {topic}.

Use this research data:
{aggregated}
{feedback_section}

Format the report with:
1. Executive Summary (2-3 sentences)
2. Key Trends (bullet points)
3. Recent Developments (bullet points)
4. Key Statistics (bullet points)
5. Real World Examples (bullet points)
6. Conclusion (2-3 sentences)

Make it professional and insightful."""

    response = llm.invoke([HumanMessage(content=prompt)])
    print("  Report written ✅")
    notify("writer", "done")
    return response.content
