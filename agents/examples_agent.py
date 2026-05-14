from urllib import response

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from callback_manager import notify 
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)

search_tool = TavilySearch(
    max_results=3,
    tavily_api_key=os.environ.get("TAVILY_API_KEY")
)

def run_examples_agent(topic: str) -> str:

    """Find real world examples for the given topic."""
    notify("examples", "running")       # ← add this line
    print("\n→ Examples Agent: Finding real world examples...")
    
    results = search_tool.invoke(
        f"real world examples use cases {topic} companies 2025"
    )
    
    prompt = f"""Find 3-4 real world examples or use cases of {topic}
    from this research:
    {results}"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    print("  Examples collection complete ✅")
    notify("examples", "done")
    return response.content