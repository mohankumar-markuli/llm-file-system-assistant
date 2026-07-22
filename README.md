# LLM File System Assistant

An intelligent, tool-calling File System Assistant powered by LLM function calling. The assistant programmatically interacts with local PDF resume documents — listing files, extracting text with metadata, searching keywords with context, and generating formatted summary files.

---

## Features

- **Core File System Tools (`fs_tools.py`)**:
  - `read_file`: Parses text content and extracts metadata (name, path, size, modification timestamp, type) from PDF, DOCX, and TXT files.
  - `list_files`: Lists directory contents with metadata and optional extension filtering (`.pdf`, `.docx`, `.txt`).
  - `write_file`: Writes content to any destination path, automatically creating parent subdirectories.
  - `search_in_file`: Executes case-insensitive keyword searches, returning exact matching lines with surrounding context.
- **LLM Function Calling Integration (`llm_file_assistant.py`)**:
  - Integrated via OpenAI / OpenRouter API using OpenAI function calling JSON schemas.
  - **Multi-Step Execution Loop**: Supports iterative multi-turn tool calling (e.g. listing directory, then reading/searching each resume sequentially, then writing output files).
- **Project Workbook (`workbook.ipynb`)**:
  - A complete, end-to-end Jupyter Notebook walking through the entire project — from setup and tool definitions to live LLM demo queries and validation tests.

---

## Project Structure

```
llm-file-system-assistant/
├── fs_tools.py             # Core file system tools module (Part A)
├── llm_file_assistant.py   # LLM integration & function calling agent (Part B)
├── workbook.ipynb          # End-to-end project walkthrough notebook
├── requirements.txt        # Project dependencies
├── .env                    # Environment configuration (API keys)
├── README.md               # Project documentation
└── resumes/                # Sample PDF resume files
    ├── resume_john_doe.pdf
    ├── resume_jane_smith.pdf
    ├── resume_bob_williams.pdf
    ├── resume_david_miller.pdf
    └── resume_eva_davis.pdf
```

---

## Setup & Installation

### 1. Clone & Setup Environment

```bash
git clone https://github.com/mohankumar-markuli/llm-file-system-assistant.git
cd llm-file-system-assistant

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys (`.env`)

Create or update the `.env` file in the root directory:

```ini
# Use OpenRouter
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here

# OR use OpenAI directly
# OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: override default model
# MODEL_NAME=openai/gpt-4o-mini
```

---

## Usage

### Option A: Run the Notebook (Recommended)

Open `workbook.ipynb` in Jupyter or VS Code and run cells in order. The notebook covers the complete project flow step-by-step:

| Step | Description |
|------|-------------|
| 1 | Project overview and structure |
| 2 | Install dependencies |
| 3 | Import libraries |
| 4 | Configure API keys |
| 5 | Generate sample PDF resumes |
| 6–9 | Define and demo all 4 file system tools |
| 10 | Define tool JSON schemas for function calling |
| 11 | Tool execution dispatcher |
| 12 | Multi-step LLM agentic loop |
| 13 | Demo — Read all resumes |
| 14 | Demo — Find Python experience |
| 15 | Demo — Create a summary file |
| 16 | Validation test suite |
| 17 | Interactive query mode |

```bash
jupyter notebook workbook.ipynb
# or open in VS Code with Jupyter extension
```

### Option B: Run the Interactive CLI

Start the interactive terminal session directly:

```bash
python llm_file_assistant.py
```

---

## Example Queries & Tool Call Demonstrations

### Query 1: List / Read Resumes
> **Input:** `Read all resumes in the resumes folder`
- **Tool Execution:** `list_files(directory="resumes")` → `read_file(filepath=...)` for each file.
- **Output:** Structured overview of all candidate resumes.

### Query 2: Search Candidates by Tech Stack
> **Input:** `Find resumes mentioning Python experience`
- **Tool Execution:** `list_files(directory="resumes")` → `search_in_file(filepath=..., keyword="Python")` for each file.
- **Output:** List of candidates with matching lines and surrounding context snippets.

### Query 3: Create a Summary File
> **Input:** `Create a summary file for resumes/resume_john_doe.pdf at summaries/john_doe_summary.txt`
- **Tool Execution:** `read_file(filepath="resumes/resume_john_doe.pdf")` → `write_file(filepath="summaries/john_doe_summary.txt", content=...)`.
- **Output:** Resume content extracted, summarized, and written to disk.

---

## Demo Video Recording Guide

When recording your 2–3 minute video demo:
1. Show the project structure and the `resumes/` folder contents (5 PDF files).
2. Open `workbook.ipynb` and run cells step-by-step, narrating each stage.
3. Demonstrate live tool calling by running the three demo query cells:
   - **Step 13** — `"Read all resumes in the resumes folder"` (observe `list_files` & `read_file` logs).
   - **Step 14** — `"Find resumes mentioning Python experience"` (observe `search_in_file` logs).
   - **Step 15** — `"Create a summary file for resumes/resume_john_doe.pdf at summaries/john_doe_summary.txt"` (observe `write_file` log and verify the output file).
4. Optionally run **Step 16** (validation tests) to confirm all tools pass.

---

## License

MIT License. Developed for LLM Function Calling & Tool Use Assignment.
