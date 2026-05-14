from graphs.sequential_graph import build_sequential_graph
from graphs.parallel_graph import build_parallel_graph
from graphs.branching_graph import build_branching_graph
from graphs.loop_graph import build_loop_graph
from callback_manager import set_callback, clear_callback

def get_initial_state(topic: str, pattern: str) -> dict:
    return {
        "topic": topic,
        "trends": "",
        "news": "",
        "statistics": "",
        "examples": "",
        "aggregated": "",
        "reflection_score": 0.0,
        "reflection_feedback": "",
        "reflection_history": [],
        "retry_count": 0,
        "final_report": "",
        "pattern": pattern,
        "selected_agent": ""
    }

def run_research(topic: str, pattern: str, callback=None) -> dict:
    """
    Main entry point — builds and runs the correct graph
    based on selected pattern.
    """
    if callback:
        set_callback(callback)

    print(f"\n{'='*60}")
    print(f"  CONTENT RESEARCH AGENT")
    print(f"  Topic: {topic}")
    print(f"  Pattern: {pattern}")
    print(f"{'='*60}")

    if pattern == "sequential":
        app = build_sequential_graph()
    elif pattern == "parallel":
        app = build_parallel_graph()
    elif pattern == "branching":
        app = build_branching_graph()
    elif pattern == "loop":
        app = build_loop_graph()
    else:
        app = build_parallel_graph()

    result = app.invoke(get_initial_state(topic, pattern))

    clear_callback()

    print(f"\n{'='*60}")
    print(f"  Research complete!")
    print(f"  Pattern used: {pattern}")
    if result.get("reflection_score"):
        print(f"  Quality score: {result['reflection_score']}")
    print(f"{'='*60}")

    return result


if __name__ == "__main__":
    print("\nCONTENT RESEARCH AGENT")
    print("="*40)

    topic = input("Enter research topic: ").strip()

    print("\nSelect pattern:")
    print("1. Sequential  — one agent at a time")
    print("2. Parallel    — all agents simultaneously")
    print("3. Branching   — router picks best agent")
    print("4. Loop        — self-reflection until quality met")

    choice = input("\nEnter choice (1-4): ").strip()

    patterns = {
        "1": "sequential",
        "2": "parallel",
        "3": "branching",
        "4": "loop"
    }

    pattern = patterns.get(choice, "parallel")
    result = run_research(topic, pattern)

    print("\nFINAL REPORT:")
    print("="*60)
    print(result["final_report"])
