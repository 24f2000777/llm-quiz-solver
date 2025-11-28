"""LangGraph agent for autonomous quiz solving."""
import logging
import os
from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from config import EMAIL, SECRET, RECURSION_LIMIT
from tools import scrape_page, download_file, run_code, send_post, install_package

logger = logging.getLogger(__name__)


# State definition
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


# Tools available to agent
TOOLS = [scrape_page, download_file, run_code, send_post, install_package]


# LLM - using ChatGoogleGenerativeAI directly
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
).bind_tools(TOOLS)

# System prompt - concise and structured
SYSTEM_PROMPT = f"""You are an autonomous quiz-solving agent.

**WORKFLOW:**
1. LOAD: Use scrape_page(url) to fetch quiz
2. PARSE: Extract task, endpoint, fields needed
3. SOLVE: Use tools (be smart about data formats)
4. SUBMIT: Use send_post() with answer
5. CHECK: If response has "url" → repeat from step 1, else return "END"

**DATA HANDLING (CRITICAL):**
- CSVs often have NO column headers - just raw numbers
- ALWAYS check first: use df.columns to see structure
- If df.columns shows [0, 1, 2...] → No headers, access by number
- For single-column data: use df[0].sum() not df['value'].sum()
- Read error messages carefully and fix immediately

**RULES:**
- Include email={EMAIL}, secret={SECRET} in all submissions
- Never resubmit if delay >= 180 seconds
- Use exact URLs from quiz pages
- Return "END" only when no "url" in response

**TOOLS:**
- scrape_page: Get HTML (works with JS)
- download_file: Save files (returns filename only)
- run_code: Execute Python (cwd=temp_files, so just use filename)
- send_post: Submit answers
- install_package: Add Python libs if needed
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages")
])

llm_with_prompt = prompt | llm


# Agent node
def agent_node(state: AgentState):
    """Execute LLM reasoning step."""
    result = llm_with_prompt.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}


# Routing logic
def route_decision(state: AgentState):
    """Decide next step based on last message."""
    last_msg = state["messages"][-1]
    
    # Check for tool calls
    tool_calls = getattr(last_msg, "tool_calls", None) or (
        last_msg.get("tool_calls") if isinstance(last_msg, dict) else None
    )
    if tool_calls:
        return "tools"
    
    # Check for END signal
    content = getattr(last_msg, "content", None) or (
        last_msg.get("content") if isinstance(last_msg, dict) else None
    )
    
    if isinstance(content, str) and content.strip() == "END":
        logger.info("Agent returned END signal")
        return END
    
    if isinstance(content, list) and content[0].get("text", "").strip() == "END":
        logger.info("Agent returned END signal")
        return END
    
    return "agent"


# Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", route_decision)

app = graph.compile()


def run_agent(url: str):
    """Run the agent on a quiz URL."""
    logger.info(f"Agent starting with URL: {url}")
    
    try:
        result = app.invoke(
            {"messages": [{"role": "user", "content": url}]},
            config={"recursion_limit": RECURSION_LIMIT}
        )
        logger.info("✅ Agent completed successfully")
        return result
    
    except Exception as e:
        logger.error(f"❌ Agent failed: {e}", exc_info=True)
        raise
