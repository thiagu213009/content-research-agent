import streamlit as st
import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Content Research Agent",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0d0f14; color: #e2e6ef; }
    .stApp > header { background-color: #0d0f14; }
    [data-testid="stSidebar"] {
        background-color: #13161d;
        border-right: 1px solid #2a2f3a;
    }
    .stTextInput input {
        background-color: #1a1e27 !important;
        border: 1px solid #2a2f3a !important;
        color: #e2e6ef !important;
        border-radius: 8px !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #4f7ef0, #7c5af0) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    .stSelectbox > div > div {
        background-color: #1a1e27 !important;
        border: 1px solid #2a2f3a !important;
        color: #e2e6ef !important;
    }
    .graph-node {
        background: #1a1e27;
        border: 1px solid #2a2f3a;
        border-radius: 10px;
        padding: 12px 20px;
        text-align: center;
        font-weight: 500;
        font-size: 14px;
        margin: 4px auto;
        color: #8b92a3;
    }
    .graph-node.active {
        border-color: #4f7ef0 !important;
        color: #4f7ef0 !important;
        background: rgba(79,126,240,0.1) !important;
        box-shadow: 0 0 12px rgba(79,126,240,0.3) !important;
    }
    .graph-node.done {
        border-color: #3dbd7a !important;
        color: #3dbd7a !important;
        background: rgba(61,189,122,0.1) !important;
    }
    .graph-node.pending { opacity: 0.35; }
    .graph-node.parallel-active {
        border-color: #f0a333 !important;
        color: #f0a333 !important;
        background: rgba(240,163,51,0.1) !important;
        box-shadow: 0 0 12px rgba(240,163,51,0.3) !important;
    }
    .graph-node.reflection-active {
        border-color: #f06060 !important;
        color: #f06060 !important;
        background: rgba(240,96,96,0.1) !important;
    }
    .parallel-label {
        text-align: center;
        color: #f0a333;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin: 4px 0;
    }
    .branch-label {
        text-align: center;
        color: #4f7ef0;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin: 4px 0;
    }
    .arrow {
        text-align: center;
        color: #2a2f3a;
        font-size: 18px;
        line-height: 1;
        margin: 2px 0;
    }
    [data-testid="stMetric"] {
        background: #1a1e27;
        border: 1px solid #2a2f3a;
        border-radius: 10px;
        padding: 12px;
    }
    .app-header {
        padding: 8px 0 20px;
        border-bottom: 1px solid #2a2f3a;
        margin-bottom: 24px;
    }
    .app-title {
        font-size: 24px;
        font-weight: 600;
        color: #e2e6ef;
    }
    .app-subtitle {
        font-size: 13px;
        color: #555d6e;
        margin-top: 4px;
    }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: #e2e6ef !important;
    }

    /* Draft / Critique / Finalize cards */
    .reflection-card {
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    .reflection-card.draft {
        background: rgba(79,126,240,0.06);
        border-left-color: #4f7ef0;
    }
    .reflection-card.critique-needs-work {
        background: rgba(240,163,51,0.06);
        border-left-color: #f0a333;
    }
    .reflection-card.critique-approved {
        background: rgba(61,189,122,0.06);
        border-left-color: #3dbd7a;
    }
    .reflection-card.finalize {
        background: rgba(51,196,196,0.06);
        border-left-color: #33c4c4;
    }
    .card-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .card-label.draft { color: #4f7ef0; }
    .card-label.critique-needs-work { color: #f0a333; }
    .card-label.critique-approved { color: #3dbd7a; }
    .card-label.finalize { color: #33c4c4; }
    .card-body {
        font-size: 13px;
        color: #8b92a3;
        line-height: 1.7;
    }
    .score-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    .score-pill.pass { background: rgba(61,189,122,0.15); color: #3dbd7a; }
    .score-pill.fail { background: rgba(240,163,51,0.15); color: #f0a333; }
</style>
""", unsafe_allow_html=True)


def get_node_class(node_states, name):
    state = node_states.get(name, "pending")
    if state == "running":
        if name in ["trends", "news", "statistics", "examples"]:
            return "graph-node parallel-active"
        elif name == "reflection":
            return "graph-node reflection-active"
        return "graph-node active"
    elif state == "done":
        return "graph-node done"
    return "graph-node pending"


def get_graph_html(pattern, node_states):
    def nc(name):
        return get_node_class(node_states, name)

    score = node_states.get("score", 0)
    retry = node_states.get("retry_count", 0)
    selected = node_states.get("selected_agent", "")

    if pattern == "sequential":
        return f"""
        <div style="display:flex;flex-direction:column;align-items:center;gap:2px;padding:20px">
            <div class="{nc('input')}" style="width:220px">🔵 User Input</div>
            <div class="arrow">↓</div>
            <div class="{nc('trends')}" style="width:220px">📈 Trends Agent</div>
            <div class="arrow">↓</div>
            <div class="{nc('news')}" style="width:220px">📰 News Agent</div>
            <div class="arrow">↓</div>
            <div class="{nc('statistics')}" style="width:220px">📊 Statistics Agent</div>
            <div class="arrow">↓</div>
            <div class="{nc('examples')}" style="width:220px">💡 Examples Agent</div>
            <div class="arrow">↓</div>
            <div class="{nc('aggregator')}" style="width:220px">⊕ Aggregator</div>
            <div class="arrow">↓</div>
            <div class="{nc('writer')}" style="width:220px">✍ Writer</div>
            <div class="arrow">↓</div>
            <div class="graph-node" style="width:120px;border-style:dashed;opacity:1">END</div>
        </div>"""

    elif pattern == "parallel":
        return f"""
        <div style="display:flex;flex-direction:column;align-items:center;gap:2px;padding:20px">
            <div class="{nc('input')}" style="width:240px">🔵 User Input</div>
            <div class="arrow">↓</div>
            <div class="{nc('planner')}" style="width:240px">⬡ Planner</div>
            <div class="arrow">↓</div>
            <div class="parallel-label">⚡ PARALLEL SUPERSTEP (ALL RUN CONCURRENTLY)</div>
            <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:4px 0">
                <div class="{nc('trends')}" style="width:130px">📈 Trends</div>
                <div class="{nc('news')}" style="width:130px">📰 News</div>
                <div class="{nc('statistics')}" style="width:130px">📊 Statistics</div>
                <div class="{nc('examples')}" style="width:130px">💡 Examples</div>
            </div>
            <div class="arrow">↓</div>
            <div class="{nc('aggregator')}" style="width:240px">⊕ Aggregator (Fan-in)</div>
            <div class="arrow">↓</div>
            <div class="{nc('writer')}" style="width:240px">✍ Writer</div>
            <div class="arrow">↓</div>
            <div class="graph-node" style="width:120px;border-style:dashed;opacity:1">END</div>
        </div>"""

    elif pattern == "branching":
        def branch_class(agent_key):
            if not selected:
                return nc(agent_key)
            if agent_key in selected:
                return nc(agent_key)
            return "graph-node pending"

        return f"""
        <div style="display:flex;flex-direction:column;align-items:center;gap:2px;padding:20px">
            <div class="{nc('input')}" style="width:240px">🔵 User Input</div>
            <div class="arrow">↓</div>
            <div class="{nc('router')}" style="width:240px">🔀 Router Agent</div>
            <div class="arrow">↓</div>
            <div class="branch-label">CONDITIONAL ROUTE (ONE BRANCH EXECUTES)</div>
            <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:4px 0">
                <div class="{branch_class('trends')}" style="width:130px">📈 Trends</div>
                <div class="{branch_class('news')}" style="width:130px">📰 News</div>
                <div class="{branch_class('statistics')}" style="width:130px">📊 Statistics</div>
                <div class="{branch_class('examples')}" style="width:130px">💡 Examples</div>
            </div>
            <div class="arrow">↓</div>
            <div class="{nc('writer')}" style="width:240px">✍ Writer</div>
            <div class="arrow">↓</div>
            <div class="graph-node" style="width:120px;border-style:dashed;opacity:1">END</div>
        </div>"""

    elif pattern == "loop":
        score_text = f"| Score: {score:.2f}" if score else ""
        retry_text = f"🔄 Retry {retry}/3" if retry > 0 else "score ≥ 0.7 → proceed | score < 0.7 → retry"
        return f"""
        <div style="display:flex;flex-direction:column;align-items:center;gap:2px;padding:20px">
            <div class="{nc('input')}" style="width:240px">🔵 User Input</div>
            <div class="arrow">↓</div>
            <div class="{nc('planner')}" style="width:240px">⬡ Planner</div>
            <div class="arrow">↓</div>
            <div class="parallel-label">⚡ PARALLEL SUPERSTEP</div>
            <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:4px 0">
                <div class="{nc('trends')}" style="width:130px">📈 Trends</div>
                <div class="{nc('news')}" style="width:130px">📰 News</div>
                <div class="{nc('statistics')}" style="width:130px">📊 Statistics</div>
                <div class="{nc('examples')}" style="width:130px">💡 Examples</div>
            </div>
            <div class="arrow">↓</div>
            <div class="{nc('aggregator')}" style="width:240px">⊕ Aggregator</div>
            <div class="arrow">↓</div>
            <div class="{nc('reflection')}" style="width:240px">◎ Self-Reflection {score_text}</div>
            <div style="text-align:center;font-size:11px;color:#555d6e;margin:2px 0">{retry_text}</div>
            <div class="arrow">↓</div>
            <div class="{nc('writer')}" style="width:240px">✍ Writer</div>
            <div class="arrow">↓</div>
            <div class="graph-node" style="width:120px;border-style:dashed;opacity:1">END</div>
        </div>"""

    return ""


def render_reflection_cards(reflection_history: list, final_report: str):
    """Render Draft → Critique → Finalize cards for loop pattern."""
    if not reflection_history:
        return

    st.markdown("---")
    st.markdown("### 🔄 Reflection Log")
    st.caption("Draft → Critique → Revise until approved")

    for entry in reflection_history:
        attempt = entry.get("attempt", 1)
        draft = entry.get("draft_summary", "")
        status = entry.get("status", "APPROVED")
        feedback = entry.get("feedback", "")
        score = entry.get("score", 0)

        if len(reflection_history) > 1:
            st.markdown(f"**Iteration {attempt}**")

        # DRAFT card
        st.markdown(f"""
        <div class="reflection-card draft">
            <div class="card-label draft">DRAFT</div>
            <div class="card-body">{draft}</div>
        </div>
        """, unsafe_allow_html=True)

        # CRITIQUE card
        score_pill_class = "pass" if score >= 0.7 else "fail"
        critique_class = "critique-approved" if status == "APPROVED" else "critique-needs-work"
        status_label = "APPROVED" if status == "APPROVED" else "NEEDS_WORK"

        st.markdown(f"""
        <div class="reflection-card {critique_class}">
            <div class="card-label {critique_class}">
                CRITIQUE
                <span class="score-pill {score_pill_class}">Score: {score:.2f}</span>
            </div>
            <div class="card-body">
                <strong>{status_label}:</strong> {feedback}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # FINALIZE card — shown after all iterations
    total = len(reflection_history)
    final_score = reflection_history[-1].get("score", 0)

    st.markdown(f"""
    <div class="reflection-card finalize">
        <div class="card-label finalize">FINALIZE</div>
        <div class="card-body">
            Final answer (after {total} iteration{'s' if total > 1 else ''})
            — quality score {final_score:.2f} ✓
        </div>
    </div>
    """, unsafe_allow_html=True)


# Session state init
for key, default in [
    ("node_states", {}),
    ("report", None),
    ("running", False),
    ("topic_value", ""),
    ("pattern_used", "parallel"),
    ("score", None),
    ("retries", 0),
    ("elapsed_time", 0),
    ("research_cache", {}),
    ("reflection_history", [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Header
st.markdown("""
<div class="app-header">
    <div class="app-title">🔬 Content Research Agent</div>
    <div class="app-subtitle">Visualising how different agent graph patterns execute using LangGraph</div>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1])

with left_col:

    st.markdown("**Agent Pattern:**")
    pattern = st.selectbox(
        "Agent Pattern",
        options=["parallel", "sequential", "branching", "loop"],
        format_func=lambda x: {
            "sequential": "Sequential (ReAct)",
            "parallel":   "Parallel (Fan-out/Fan-in)",
            "branching":  "Branching (Router)",
            "loop":       "Loop (Reflexion)"
        }[x],
        label_visibility="collapsed",
        key="pattern_select"
    )

    pattern_desc = {
        "sequential": "Agents run one at a time in sequence",
        "parallel":   "4 agents run concurrently — Fan-out/Fan-in",
        "branching":  "Router picks the best single agent",
        "loop":       "Research → Reflect → Retry until score ≥ 0.7"
    }
    st.caption(pattern_desc[pattern])

    st.markdown("**Enter your research topic:**")

    topic = st.text_input(
        "Research Topic",
        value=st.session_state.topic_value,
        placeholder="e.g. Agentic AI trends in enterprise 2025",
        label_visibility="collapsed"
    )
    st.session_state.topic_value = topic

    st.caption("Try asking:")
    suggestions = [
        "Agentic AI 2025", "LangGraph agents",
        "RAG production",  "RPA + AI trends",
        "GenAI enterprise", "MCP protocol"
    ]
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"chip_{i}", use_container_width=True):
                st.session_state.topic_value = s
                st.rerun()

    st.markdown("")
    run_clicked = st.button(
        "▶ Run Agent",
        use_container_width=True,
        disabled=st.session_state.running
    )

with right_col:
    st.markdown("**Agent Graph Flow**")
    graph_placeholder = st.empty()
    graph_placeholder.markdown(
        get_graph_html(pattern, st.session_state.node_states),
        unsafe_allow_html=True
    )

# Run research
if run_clicked:
    current_topic = st.session_state.topic_value.strip()
    if not current_topic:
        st.warning("Please enter a research topic first.")
    else:
        cache_key = f"{current_topic}|{pattern}"

        if cache_key in st.session_state.research_cache:
            cached = st.session_state.research_cache[cache_key]
            st.session_state.node_states = cached["node_states"]
            st.session_state.report = cached["report"]
            st.session_state.score = cached["score"]
            st.session_state.retries = cached["retries"]
            st.session_state.elapsed_time = cached["elapsed_time"]
            st.session_state.reflection_history = cached.get("reflection_history", [])
            st.session_state.pattern_used = pattern
            st.info(f"⚡ Loaded from cache (originally {cached['elapsed_time']}s)")
            st.rerun()

        else:
            from research_engine import run_research

            st.session_state.node_states = {"input": "done"}
            st.session_state.running = True
            st.session_state.report = None
            st.session_state.reflection_history = []

            local_node_states = {"input": "done"}
            progress_messages = []
            start_time = time.time()

            def on_agent_update(node, status, message=""):
                if status == "running":
                    local_node_states[node] = "running"
                    progress_messages.append(f"⏳ **{node.upper()}** starting...")
                elif status == "done":
                    local_node_states[node] = "done"
                    if "Score" in message:
                        score_val = float(message.split(":")[1].strip())
                        local_node_states["score"] = score_val
                        if score_val < 0.7:
                            retry = local_node_states.get("retry_count", 0) + 1
                            local_node_states["retry_count"] = retry
                            progress_messages.append(
                                f"🔄 **REFLECTION** score: {score_val:.2f} — retrying {retry}/3..."
                            )
                        else:
                            progress_messages.append(
                                f"✅ **REFLECTION** score: {score_val:.2f} — quality passed!"
                            )
                        return
                    progress_messages.append(f"✅ **{node.upper()}** complete")

            with st.status(
                f"🔬 Running **{pattern}** on: *{current_topic}*...",
                expanded=True
            ) as status_box:

                pattern_steps = {
                    "sequential": "Trends → News → Statistics → Examples → Aggregator → Writer",
                    "parallel":   "[Trends + News + Statistics + Examples] → Aggregator → Writer",
                    "branching":  "Router → Best Agent → Writer",
                    "loop":       "[Parallel Research] → Aggregator → Reflection ↺ → Writer"
                }
                st.write(f"**Flow:** `{pattern_steps.get(pattern, '')}`")
                st.divider()

                progress_placeholder = st.empty()
                keep_updating = [True]

                def update_display():
                    while keep_updating[0]:
                        if progress_messages:
                            progress_placeholder.markdown(
                                "\n\n".join(progress_messages[-10:])
                            )
                        time.sleep(0.3)

                display_thread = threading.Thread(target=update_display, daemon=True)
                display_thread.start()

                result = run_research(current_topic, pattern, callback=on_agent_update)

                keep_updating[0] = False
                time.sleep(0.4)

                elapsed = round(time.time() - start_time, 1)
                progress_placeholder.markdown("\n\n".join(progress_messages))

                status_box.update(
                    label=f"✅ Research complete in {elapsed}s",
                    state="complete",
                    expanded=False
                )

            local_node_states["writer"] = "done"
            reflection_history = result.get("reflection_history", [])

            st.session_state.node_states = local_node_states
            st.session_state.report = result["final_report"]
            st.session_state.score = result.get("reflection_score")
            st.session_state.retries = result.get("retry_count", 0)
            st.session_state.elapsed_time = elapsed
            st.session_state.pattern_used = pattern
            st.session_state.reflection_history = reflection_history
            st.session_state.running = False

            st.session_state.research_cache[cache_key] = {
                "node_states": local_node_states,
                "report": result["final_report"],
                "score": result.get("reflection_score"),
                "retries": result.get("retry_count", 0),
                "elapsed_time": elapsed,
                "reflection_history": reflection_history
            }

            st.rerun()

# Update graph
graph_placeholder.markdown(
    get_graph_html(
        st.session_state.pattern_used,
        st.session_state.node_states
    ),
    unsafe_allow_html=True
)

# Show report
if st.session_state.report:

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pattern", st.session_state.pattern_used.capitalize())
    with col2:
        agents_map = {"parallel": 8, "sequential": 7, "branching": 3, "loop": 9}
        st.metric("Agents Run", agents_map.get(st.session_state.pattern_used, 7))
    with col3:
        score = st.session_state.score
        st.metric("Quality Score", f"{score:.2f}" if score else "N/A")
    with col4:
        st.metric("Time Taken", f"{st.session_state.elapsed_time}s")

    # Show reflection cards for loop pattern only
    if st.session_state.pattern_used == "loop" and st.session_state.reflection_history:
        render_reflection_cards(
            st.session_state.reflection_history,
            st.session_state.report
        )

    st.markdown("---")

    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("📄 Research Report")
    with col2:
        st.download_button(
            "⬇ Download",
            data=st.session_state.report,
            file_name=f"report_{st.session_state.topic_value[:20]}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown(st.session_state.report)