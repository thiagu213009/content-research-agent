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

def run_trends_agent(topic: str) -> str:
    """Research latest trends for the given topic."""
    notify("trends", "running") 
    print("\n→ Trends Agent: Researching latest trends...")
    
    results = search_tool.invoke(f"latest trends {topic} 2025")
    
    prompt = f"""Summarise the key trends about {topic} 
    from this research in 3-4 bullet points:
    {results}"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    print("  Trends research complete ✅")
    notify("trends", "done") 
    return response.content