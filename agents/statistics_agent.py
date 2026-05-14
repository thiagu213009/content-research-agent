from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from callback_manager import notify

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)

search_tool = TavilySearch(
    max_results=1,
    tavily_api_key=os.environ.get("TAVILY_API_KEY")
)

def run_statistics_agent(topic: str) -> str:
    """Gather statistics and data for the given topic."""
    notify("statistics", "running")
    print("\n→ Statistics Agent: Gathering statistics...")
    
    results = search_tool.invoke(f"statistics data numbers {topic} 2025")
    
    prompt = f"""Extract key statistics and numbers about {topic}
    from this research in 3-4 bullet points:
    {results}"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    print("  Statistics gathering complete ✅")
    notify("statistics", "done")
    return response.content