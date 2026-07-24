# LLM File System Assistant

An intelligent, tool-calling File System Assistant powered by LLM function calling. The assistant programmatically interacts with local PDF resume documents — listing files, extracting text with metadata, searching keywords with context, and generating formatted summary files.

---

## Project Structure

```text
llm-file-system-assistant/
├── workbook.ipynb          # End-to-end standalone project notebook (Part A & Part B)
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

## Key Features in `workbook.ipynb`

- **Part A — Core File System Tools**:
  - `read_file`: Parses text content and metadata (`name`, `path`, `size_bytes`, `type`, `modified_date`) from `.pdf`, `.txt`, `.docx` files or entire directories.
  - `list_files`: Lists directory contents with metadata and optional extension filtering.
  - `write_file`: Writes content to any destination path, automatically creating parent directories.
  - `search_in_file`: Executes case-insensitive keyword searches in a file or directory, returning matching lines with context.

- **Part B — LLM Integration & Function Calling**:
  - Structured OpenAI tool JSON schemas & dispatcher function.
  - Autonomous multi-step LLM tool-calling loop (`SystemMessage`, `UserMessage`, `ToolMessage`).
  - Integrated with OpenAI & OpenRouter API endpoints.

---

## Setup & Installation

### 1. Setup Environment

```bash
# Create virtual environment
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

Ensure `.env` contains an API key:

```ini
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here

# OR OpenAI API Key
# OPENAI_API_KEY=sk-your-openai-api-key-here
```

---

## Running the Workbook

Open `workbook.ipynb` in Jupyter Notebook or VS Code and execute the cells sequentially:

```bash
jupyter notebook workbook.ipynb
```

### Notebook Workflow Steps:
1. **Overview & Setup**
2. **Dependencies & Import Libraries**
3. **Configure API Keys**
4. **Generate Sample Resumes**
5. **Part A: Core File System Tools (`read_file`, `list_files`, `write_file`, `search_in_file`)**
6. **Part B: LLM Tool Schemas & Multi-step Agentic Loop**
7. **Demonstration & Example Queries**:
   - *"Read all resumes in the resumes folder"*
   - *"Find resumes mentioning Python experience"*
   - *"Create a summary file for resume_john_doe.pdf"*
8. **Validation Test Suite & Interactive Query Loop**

---

## License

MIT License. Developed for LLM Function Calling & Tool Use Assignment.
