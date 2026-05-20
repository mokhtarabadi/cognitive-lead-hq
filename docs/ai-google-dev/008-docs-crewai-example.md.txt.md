---
title: CrewAI Multi-Agent Tutorial
url: https://ai.google.dev/gemini-api/docs/crewai-example.md.txt
source: llms
fetched_at: 2026-04-29T11:17:20.453297609-03:00
rendered_js: false
word_count: 246
summary: Build a multi-agent system using CrewAI to analyze customer support data and generate executive reports.
tags:
    - crewai
    - ai-agents
    - multi-agent-systems
    - gemini-llm
    - data-analysis
    - workflow-automation
category: tutorial
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
[CrewAI](https://docs.crewai.com/introduction) orchestrates autonomous AI agents that collaborate to achieve complex goals. This example builds a multi-agent system for analyzing customer support data, identifying issues, and proposing process improvements using Gemini 3 Flash, generating a report for the COO.

The crew performs:

1. Fetch and analyze customer support data (simulated)
2. Identify recurring problems and process bottlenecks
3. Suggest actionable improvements
4. Compile findings into a concise COO report

## Prerequisites

- Gemini API key ([get from Google AI Studio](https://aistudio.google.com/app/apikey))
- `pip install "crewai[tools]"`

Set `GEMINI_API_KEY` environment variable and configure CrewAI:

```python
import os
from crewai import LLM

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_llm = LLM(
    model='gemini/gemini-3-flash-preview',
    api_key=gemini_api_key,
    temperature=1.0  # Gemini 3 recommended temperature
)
```

## Define Components

CrewAI applications use **Tools**, **Agents**, **Tasks**, and **Crew**.

### Tools

Tools are capabilities for agents to interact with the outside world. Define a placeholder tool simulating data fetching (real app connects to database, API, or file system).

```python
from crewai.tools import BaseTool

class CustomerSupportDataTool(BaseTool):
    name: str = "Customer Support Data Fetcher"
    description: str = (
        "Fetches recent customer support interactions, tickets, and feedback. "
        "Returns a summary string.")

    def _run(self, argument: str) -> str:
        # In a real scenario, query database or API.
        # For this example, return simulated data.
        print(f"--- Fetching data for query: {argument} ---")
        return (
            """Recent Support Data Summary:
- 50 tickets related to 'login issues'. High resolution time (avg 48h).
- 30 tickets about 'billing discrepancies'. Mostly resolved within 12h.
- 20 tickets on 'feature requests'. Often closed without resolution.
- Frequent feedback mentions 'confusing user interface' for password reset.
- High volume of calls related to 'account verification process'.
- Sentiment analysis shows growing frustration with 'login issues' resolution time.
- Support agent notes indicate difficulty reproducing 'login issues'."""
        )

support_data_tool = CustomerSupportDataTool()
```

For more on tools, see [CrewAI tools guide](https://docs.crewai.com/concepts/tools).

### Agents

Agents are AI workers with specific `role`, `goal`, `backstory`, assigned `llm`, and optional `tools`.

```python
from crewai import Agent

# Agent 1: Data analyst
data_analyst = Agent(
    role='Customer Support Data Analyst',
    goal='Analyze customer support data to identify trends, recurring issues, and key pain points.',
    backstory="""You are an expert data analyst specializing in customer support operations.
You identify patterns and quantify problems from raw support data.""",
    verbose=True,
    allow_delegation=False,
    tools=[support_data_tool],
    llm=gemini_llm
)

# Agent 2: Process optimizer
process_optimizer = Agent(
    role='Process Optimization Specialist',
    goal='Identify bottlenecks and inefficiencies in support processes based on analysis. Propose actionable improvements.',
    backstory="""You are a specialist in optimizing business processes, particularly in customer support.
You excel at pinpointing root causes of delays and suggesting concrete solutions.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# Agent 3: Report writer
report_writer = Agent(
    role='Executive Report Writer',
    goal='Compile analysis and improvement suggestions into a concise, actionable report for the COO.',
    backstory="""You are skilled at creating executive summaries and reports.
You focus on clarity, conciseness, and highlighting critical information and recommendations for senior leadership.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)
```

For more on agents, see [CrewAI agents guide](https://docs.crewai.com/concepts/agents).

### Tasks

Tasks define assignments with `description`, `expected_output`, and assigned `agent`. Tasks run sequentially by default and include context from previous tasks.

```python
from crewai import Task

# Task 1: Analyze data
analysis_task = Task(
    description="""Fetch and analyze the latest customer support interaction data (tickets, feedback, call logs)
focusing on the last quarter. Identify the top 3-5 recurring issues, quantify their frequency
and impact (e.g., resolution time, customer sentiment). Use the Customer Support Data Fetcher tool.""",
    expected_output="""A summary report detailing:
- Top 3-5 recurring issues with frequency
- Average resolution times
- Key customer pain points
- Notable trends in sentiment or agent observations.""",
    agent=data_analyst
)

# Task 2: Identify bottlenecks and suggest improvements
optimization_task = Task(
    description="""Based on the Data Analyst report, identify primary bottlenecks in support processes.
Propose 2-3 concrete, actionable process improvements. Consider impact and ease of implementation.""",
    expected_output="""A concise list of:
- Main process bottlenecks (e.g., lack of documentation, complex escalation, UI issues)
- 2-3 specific recommendations (e.g., update knowledge base, simplify password reset UI, implement proactive monitoring)""",
    agent=process_optimizer
)

# Task 3: Compile COO report
report_task = Task(
    description="""Compile findings from Data Analyst and Process Optimization Specialist into a concise executive report for the COO:
1. Most critical customer support issues (with data points)
2. Key process bottlenecks
3. Recommended improvements
Format professionally with clear headings and bullet points.""",
    expected_output="""A well-structured executive report (max 1 page) with actionable insights for the COO.""",
    agent=report_writer
)
```

For more on tasks, see [CrewAI tasks guide](https://docs.crewai.com/concepts/tasks).

### Crew

The `Crew` brings agents and tasks together, defining the workflow (e.g., sequential).

```python
from crewai import Crew, Process

support_analysis_crew = Crew(
    agents=[data_analyst, process_optimizer, report_writer],
    tasks=[analysis_task, optimization_task, report_task],
    process=Process.sequential,
    verbose=True
)
```

## Run the Crew

```python
print("--- Starting Customer Support Analysis Crew ---")
result = support_analysis_crew.kickoff(inputs={'data_query': 'last quarter support data'})

print("--- Crew Execution Finished ---")
print("--- Final Report for COO ---")
print(result)
```

The script executes: `Data Analyst` fetches data → `Process Optimizer` analyzes findings → `Report Writer` compiles the final report.

`verbose=True` shows detailed thought process and actions of each agent.

For more on CrewAI, see [CrewAI introduction](https://docs.crewai.com/introduction).