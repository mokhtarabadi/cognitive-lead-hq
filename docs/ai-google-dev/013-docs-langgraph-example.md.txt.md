---
title: Build a ReAct Agent with LangGraph
url: https://ai.google.dev/gemini-api/docs/langgraph-example.md.txt
source: llms
fetched_at: 2026-04-29T11:16:24.28740228-03:00
rendered_js: false
word_count: 266
summary: Build a stateful ReAct agent using LangGraph with state management, tool integration, and graph construction.
tags:
    - langgraph
    - react-agent
    - llm-agents
    - state-management
    - tool-calling
    - workflow-automation
category: tutorial
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
LangGraph builds stateful LLM applications, ideal for constructing [ReAct (Reasoning and Acting) Agents](https://arxiv.org/abs/2210.03629). ReAct agents combine LLM reasoning with action execution, iteratively thinking, using tools, and acting on observations.

LangGraph provides a prebuilt ReAct agent ([`create_react_agent`](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)) for more control and customization.

## Core Components

LangGraph models agents as graphs:

| Component | Description |
|---|---|
| **State** | Shared data structure (TypedDict or Pydantic BaseModel) representing current application snapshot |
| **Nodes** | Encode agent logic. Receive State, perform computation/side-effects, return updated State |
| **Edges** | Define next Node to execute based on current State (conditional logic and fixed transitions) |

Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

Install dependencies:

```bash
pip install langgraph langchain-google-genai geopy requests
```

Set `GEMINI_API_KEY` environment variable:

```python
import os
api_key = os.getenv("GEMINI_API_KEY")
```

## Example: Weather Agent

This guide creates an agent that finds current weather for a specified location.

The `State` maintains conversation history (list of messages) and a step counter.

LangGraph provides `add_messages` helper for updating state message lists (handles updates by message ID, defaults to append-only for new messages).

```python
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int
```

> [!NOTE]
> Since a list of messages in state is common, `MessagesState` prebuilt state exists. This example lists messages explicitly.

## Define Weather Tool

```python
from langchain_core.tools import tool
from geopy.geocoders import Nominatim
from pydantic import BaseModel, Field
import requests

geolocator = Nominatim(user_agent="weather-app")

class SearchInput(BaseModel):
    location: str = Field(description="The city and state, e.g., San Francisco")
    date: str = Field(description="The forecasting date (yyyy-mm-dd)")

@tool("get_weather_forecast", args_schema=SearchInput, return_direct=True)
def get_weather_forecast(location: str, date: str):
    """Retrieves weather using Open-Meteo API.
    Takes a location (city) and date (yyyy-mm-dd).
    Returns: Dict with time and temperature for each hour.
    """
    # Note: Colab may experience rate limiting. Use exclusive-access machine if needed.
    location = geolocator.geocode(location)
    if location:
        try:
            response = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&hourly=temperature_2m&start_date={date}&end_date={date}"
            )
            data = response.json()
            return dict(zip(data["hourly"]["time"], data["hourly"]["temperature_2m"]))
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Location not found"}

tools = [get_weather_forecast]
```

## Initialize Model and Bind Tools

```python
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=1.0,
    max_retries=2,
    google_api_key=api_key,
)

model = llm.bind_tools([get_weather_forecast])

# Test with tools
res = model.invoke(f"What is the weather in Berlin on {datetime.today()}?")
print(res)
```

## Define Nodes and Edges

| Node | Purpose |
|---|---|
| `call_tool` | Executes your tool method (use LangGraph's prebuilt [ToolNode](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)) |
| `call_model` | Uses `model_with_tools` to call the model |

| Edge | Purpose |
|---|---|
| `should_continue` | Decides whether to call tool or model |

You can add more nodes (structured output, self-verification/reflection) as needed.

```python
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig

tools_by_name = {tool.name: tool for tool in tools}

def call_tool(state: AgentState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=tool_result,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}

def call_model(state: AgentState, config: RunnableConfig):
    response = model.invoke(state["messages"], config)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    if not messages[-1].tool_calls:
        return "end"
    return "continue"
```

## Assemble Graph

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# 1. Add nodes
workflow.add_node("llm", call_model)
workflow.add_node("tools", call_tool)

# 2. Set entrypoint as `llm`
workflow.set_entry_point("llm")

# 3. Add conditional edge after `llm`
workflow.add_conditional_edges(
    "llm",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

# 4. Add edge after `tools` → `llm`
workflow.add_edge("tools", "llm")

# Compile and visualize
graph = workflow.compile()

from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))
```

![png](https://ai.google.dev/static/gemini-api/docs/images/langgraph-react-agent_16_0.png)

## Run the Agent

```python
from datetime import datetime

inputs = {"messages": [("user", f"What is the weather in Berlin on {datetime.today()}?")]}

for state in graph.stream(inputs, stream_mode="values"):
    last_message = state["messages"][-1]
    last_message.pretty_print()
```

Continue conversation:

```python
state["messages"].append(("user", "Would it be warmer in Munich?"))

for state in graph.stream(state, stream_mode="values"):
    last_message = state["messages"][-1]
    last_message.pretty_print()
```