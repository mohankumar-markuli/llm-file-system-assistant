import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI
import fs_tools

# Fix Windows console UTF-8 output issue
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables from .env file
load_dotenv()

def get_openai_client():
    """Configure and return OpenAI client pointing to OpenAI or OpenRouter based on .env."""
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if openrouter_key:
        print("[System] Using OpenRouter API client.")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key
        ), os.environ.get("MODEL_NAME", "openai/gpt-4o-mini")
    elif openai_key:
        print("[System] Using OpenAI API client.")
        return OpenAI(
            api_key=openai_key
        ), os.environ.get("MODEL_NAME", "gpt-4o-mini")
    else:
        print("ERROR: Neither OPENROUTER_API_KEY nor OPENAI_API_KEY found in environment variables.")
        print("Please configure your .env file with a valid API key.")
        sys.exit(1)

client, MODEL = get_openai_client()

# Define JSON schemas for tools according to OpenAI / OpenRouter function calling spec
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a resume file (.pdf, .txt, .docx) and extract text content along with metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The absolute or relative file path to read."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in a directory, optionally filtering by extension (e.g. '.pdf', '.txt', '.docx').",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory path to scan (e.g. 'resumes')."
                    },
                    "extension": {
                        "type": "string",
                        "description": "Optional file extension to filter results by (e.g., '.pdf', '.txt', '.docx')."
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a destination file, creating directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path of the destination file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "The textual content to write into the file."
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Perform a case-insensitive keyword search in a file and return matching lines with context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The file path to search inside."
                    },
                    "keyword": {
                        "type": "string",
                        "description": "The keyword or phrase to search for."
                    }
                },
                "required": ["filepath", "keyword"]
            }
        }
    }
]

def execute_tool_call(tool_call):
    """Execute the Python tool function matching the LLM's requested tool call."""
    function_name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments)
    except Exception as parse_err:
        print(f"[Error] Failed to parse tool arguments: {parse_err}")
        return json.dumps({"status": "failed", "error": f"Invalid JSON arguments: {parse_err}"})

    print(f"\n[Tool Execution] Calling '{function_name}' with args: {json.dumps(arguments)}")

    try:
        if function_name == "read_file":
            result = fs_tools.read_file(arguments.get("filepath"))
        elif function_name == "list_files":
            result = fs_tools.list_files(arguments.get("directory"), arguments.get("extension"))
        elif function_name == "write_file":
            result = fs_tools.write_file(arguments.get("filepath"), arguments.get("content"))
        elif function_name == "search_in_file":
            result = fs_tools.search_in_file(arguments.get("filepath"), arguments.get("keyword"))
        else:
            result = {"status": "failed", "error": f"Unknown tool function: {function_name}"}
    except Exception as e:
        result = {"status": "failed", "error": str(e)}

    # Truncate output logging if content is huge
    log_summary = str(result)
    if len(log_summary) > 250:
        log_summary = log_summary[:250] + "... [truncated]"
    print(f"[Tool Output] -> {log_summary}")

    return json.dumps(result)

def run_assistant(query: str, max_iterations: int = 10):
    """
    Run the LLM assistant loop with tool calling capability.
    Supports multi-step function calls (e.g. listing files then reading/searching them).
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI File System Assistant capable of reading, searching, listing, and writing files. "
                "You have access to specialized file system tools: list_files, read_file, search_in_file, and write_file. "
                "When asked to perform tasks on files (such as reading resumes, searching for candidate experience, or creating summary files), "
                "use the appropriate tools to inspect file contents before giving a response. "
                "Be thorough, structured, and helpful."
            )
        },
        {"role": "user", "content": query}
    ]

    print("\n" + "=" * 70)
    print(f"[User Query]: {query}")
    print("=" * 70)

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Append assistant message requesting tool calls
            messages.append(response_message)

            for tool_call in tool_calls:
                tool_result_json = execute_tool_call(tool_call)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": tool_result_json
                })
        else:
            # Final text response from assistant
            final_answer = response_message.content
            print("\n[Assistant Response]:\n")
            print(final_answer)
            print("=" * 70 + "\n")
            return final_answer

    print("\n[Warning]: Maximum tool iteration limit reached.")
    return "Maximum tool execution iterations reached."

if __name__ == "__main__":
    print("==========================================================")
    print("      LLM File System Assistant                           ")
    print("==========================================================")
    print("Available Commands:")
    print("  - Type any natural language file query")
    print("  - Type 'demo' to run standard demo queries")
    print("  - Type 'exit' or 'quit' to end session\n")

    while True:
        try:
            user_input = input("Enter your query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        if user_input.lower() == 'demo':
            demo_queries = [
                "Read all resumes in the resumes folder",
                "Find resumes mentioning Python experience",
                "Create a summary file for resume_john_doe.pdf at summaries/john_doe_summary.txt"
            ]
            for dq in demo_queries:
                run_assistant(dq)
        else:
            run_assistant(user_input)