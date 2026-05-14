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
    max_results=3,
    tavily_api_key=os.environ.get("TAVILY_API_KEY")
)

def run_news_agent(topic: str) -> str:
    """Collect recent news for the given topic."""
    
    notify("news", "running")
    print("\n→ News Agent: Collecting recent news...")
    
    results = search_tool.invoke(f"recent news {topic} 2025")
    
    prompt = f"""Summarise the latest news about {topic}
    from this research in 3-4 bullet points:
    {results}"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    print("  News collection complete ✅")
    notify("news", "done")
    return response.content