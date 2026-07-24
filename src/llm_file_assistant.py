"""
src/llm_file_assistant.py — LLM Integration & Function Calling Agent (Part B)

Integrates file system tools with LangChain ChatOpenAI / OpenRouter API.
Supports multi-turn tool calling and returns agent trace details for web & CLI interfaces.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

# Import fs_tools using package import with fallback
try:
    from src import fs_tools
except ImportError:
    import fs_tools

# Fix Windows console UTF-8 output issue
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables
load_dotenv()

# Define LangChain tools
@tool
def read_file(filepath: str) -> str:
    """Read a single file (.pdf, .txt, .docx) OR all documents in a directory at once. Extracts text content, metadata, and candidate names."""
    result = fs_tools.read_file(filepath)
    return json.dumps(result)

@tool
def list_files(directory: str, extension: str = None) -> str:
    """List all files in a directory, optionally filtering by extension (e.g. '.pdf', '.txt', '.docx')."""
    result = fs_tools.list_files(directory, extension)
    return json.dumps(result)

@tool
def write_file(filepath: str, content: str) -> str:
    """Write text content to a destination file, creating directories if needed."""
    result = fs_tools.write_file(filepath, content)
    return json.dumps(result)

@tool
def search_in_file(filepath: str, keyword: str) -> str:
    """Perform a case-insensitive keyword search in a file or entire directory and return matching lines with context."""
    result = fs_tools.search_in_file(filepath, keyword)
    return json.dumps(result)

tools = [read_file, list_files, write_file, search_in_file]
tools_by_name = {t.name: t for t in tools}

def get_llm_model():
    """Configure and return LangChain ChatOpenAI instance pointing to OpenAI or OpenRouter based on .env."""
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if openrouter_key:
        model_name = os.environ.get("MODEL_NAME", "openai/gpt-4o-mini")
        return ChatOpenAI(
            model=model_name,
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
    elif openai_key:
        model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
        return ChatOpenAI(
            model=model_name,
            openai_api_key=openai_key
        )
    else:
        raise EnvironmentError("No API key found. Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file.")

def run_assistant_agent(query: str, max_iterations: int = 10):
    """
    Runs the agent and returns a tuple (final_answer, tool_execution_logs).
    Used by Streamlit web UI and CLI.
    """
    llm = get_llm_model()
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(
            content=(
                "You are an AI File System Assistant capable of inspecting individual files as well as entire directories of documents. "
                "You have access to specialized tools: read_file (reads a single file or ALL files in a directory at once), list_files, search_in_file, and write_file. "
                "When asked to perform tasks or answer queries about candidates/documents in a folder (e.g. 'resumes'), "
                "use read_file(filepath='resumes') to inspect all files in that directory at once. "
                "Always identify and respond with the specific related person's name (e.g. 'Alice Harper', 'John Doe', 'Marcus Vane') along with their details. "
                "When requested to create summary or recommendation files, generate thorough reports and write them using write_file."
            )
        ),
        HumanMessage(content=query)
    ]

    tool_logs = []

    for iteration in range(max_iterations):
        response_message = llm_with_tools.invoke(messages)
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                selected_tool = tools_by_name.get(tool_name)
                if selected_tool:
                    try:
                        tool_result_str = selected_tool.invoke(tool_args)
                    except Exception as e:
                        tool_result_str = json.dumps({"status": "failed", "error": str(e)})
                else:
                    tool_result_str = json.dumps({"status": "failed", "error": f"Unknown tool: {tool_name}"})

                tool_logs.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": tool_result_str
                })

                messages.append(ToolMessage(content=tool_result_str, tool_call_id=tool_id, name=tool_name))
        else:
            final_answer = response_message.content
            return final_answer, tool_logs

    return "Maximum iteration limit reached.", tool_logs

def run_assistant(query: str, max_iterations: int = 10):
    """CLI runner function."""
    print("\n" + "=" * 70)
    print(f"[User Query]: {query}")
    print("=" * 70)

    try:
        answer, logs = run_assistant_agent(query, max_iterations)
        for log in logs:
            print(f"\n[Tool Execution] Calling '{log['tool']}' with args: {json.dumps(log['args'])}")
            res_summary = log['result']
            if len(res_summary) > 250:
                res_summary = res_summary[:250] + "... [truncated]"
            print(f"[Tool Output] -> {res_summary}")

        print("\n[Assistant Response]:\n")
        print(answer)
        print("=" * 70 + "\n")
        return answer
    except Exception as e:
        print(f"Error executing agent: {e}")
        return str(e)

if __name__ == "__main__":
    print("==========================================================")
    print("      LLM File System Assistant CLI                       ")
    print("==========================================================")
    while True:
        try:
            inp = input("Enter query (or 'exit'): ").strip()
            if not inp or inp.lower() == 'exit':
                break
            run_assistant(inp)
        except (KeyboardInterrupt, EOFError):
            break
