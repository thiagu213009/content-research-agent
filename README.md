cd ContentResearch
cat > README.md << 'EOF'
---
title: Content Research Agent
emoji: 🔬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Content Research Agent

AI-powered research agent with 4 different execution patterns.

## Patterns
- **Sequential** — Agents run one at a time
- **Parallel** — Fan-out/Fan-in, all agents simultaneously
- **Branching** — Router picks best single agent
- **Loop** — Self-reflection until quality meets threshold

## Tech Stack
- LangGraph, Tavily, GPT-4o-mini, Streamlit, LangSmith
EOF