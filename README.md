# 📄 LLM File System Assistant

An intelligent, tool-calling File System Assistant powered by LLM function calling, LangChain, and RAG workflows. The assistant programmatically interacts with local PDF resume documents — listing files, extracting text with metadata, searching keywords with context, and generating formatted summary reports.

---

## 🗂️ Clean Architecture & Project Structure

All Python source code is cleanly organized inside the `src/` directory.

```text
llm-file-system-assistant/
├── src/                        # 📦 Modular Source Code Package
│   ├── __init__.py             # Package initializer
│   ├── fs_tools.py             # Part A: Core file system tools module
│   ├── llm_file_assistant.py   # Part B: LangChain agent logic & tool calling
│   └── app.py                  # Streamlit Web Application interface
├── workbook.ipynb              # Standalone end-to-end project notebook (Root)
├── requirements.txt            # Project dependencies (includes Streamlit)
├── .env                    # Environment configuration (API keys)
├── README.md               # Complete project documentation & execution guide
└── resumes/                # 10 Sample PDF candidate resume files
    ├── resume_alice_harper.pdf
    ├── resume_bob_williams.pdf
    ├── resume_clara_bennett.pdf
    ├── resume_david_miller.pdf
    ├── resume_elena_rostova.pdf
    ├── resume_eva_davis.pdf
    ├── resume_jane_smith.pdf
    ├── resume_john_doe.pdf
    ├── resume_marcus_vane.pdf
    └── resume_samuel_brooks.pdf
```

---

## 🎯 Learning Objectives & Core Features

### Part A: Core File System Tools (`src/fs_tools.py`)
- **`read_file(filepath: str) -> dict`**: Parses text content & metadata from `.pdf`, `.txt`, `.docx` files or entire directories at once.
- **`list_files(directory: str, extension: str = None) -> list`**: Lists directory files with metadata and optional extension filtering.
- **`write_file(filepath: str, content: str) -> dict`**: Writes text to destination paths, automatically creating parent directories.
- **`search_in_file(filepath: str, keyword: str) -> dict`**: Case-insensitive keyword search returning matching lines with surrounding context snippets.

### Part B: LLM Integration & RAG Pipeline (`src/llm_file_assistant.py`)
- Integrated with **LangChain Core & OpenAI / OpenRouter API**.
- Multi-step agentic tool calling loop (`bind_tools`) that reads files, searches candidate profiles, and writes summary reports to disk based on user queries.

### 💻 Interactive Streamlit Web Application (`src/app.py`)
- **Real-Time Agent Chat**: Conversational UI with interactive tool execution tracing (function names, arguments, raw JSON outputs).
- **Quick Benchmark Presets**: Single-click buttons for standard assignment queries.
- **Document Explorer & Viewer**: Inspect candidate resumes (`.pdf`, `.docx`, `.txt`) with text previews and metadata metrics.
- **Keyword Search Tool**: Dedicated search bar with line context snippet highlights.
- **File Upload Tool**: Drag-and-drop resume upload tool saving directly into `resumes/`.

---

## 🚀 Setup & Execution Guide

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/mohankumar-markuli/llm-file-system-assistant.git
cd llm-file-system-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys (`.env`)

Create or verify the `.env` file in the root directory:

```ini
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here

# OR OpenAI API Key
# OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional model name (defaults to openai/gpt-4o-mini)
MODEL_NAME=openai/gpt-4o-mini
```

---

## 💻 Running the Application Options

### Option 1: Streamlit Web Application (Recommended)

Run the Streamlit app directly from `src/app.py`:

```bash
streamlit run src/app.py
```

### Option 2: Standalone Jupyter Notebook (`workbook.ipynb`)

Open the standalone project notebook in VS Code or Jupyter:

```bash
jupyter notebook workbook.ipynb
```
*Run cells sequentially from top to bottom.*

### Option 3: Terminal CLI Mode (`src/llm_file_assistant.py`)

Run the interactive CLI agent in your terminal:

```bash
python -m src.llm_file_assistant
```

---

## 🧪 Benchmark Query Demonstrations

| Query | Tools Executed | Expected Output |
|---|---|---|
| *"Read all resumes in the resumes folder"* | `read_file(filepath="resumes")` | Returns candidate profiles and summaries for all 10 resumes. |
| *"Find resumes mentioning Python experience"* | `search_in_file(filepath="resumes", keyword="Python")` | Returns matching candidates (John Doe, Jane Smith, Eva Davis) with line snippets. |
| *"Create a summary file for resume_john_doe.pdf"* | `read_file` → `write_file` | Synthesizes an executive summary and writes to `summaries/john_doe_summary.txt`. |

---

## 📜 License

MIT License. Developed for LLM Function Calling & Tool Use Assignment.
