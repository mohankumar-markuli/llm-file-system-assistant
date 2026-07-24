"""
src/app.py — Streamlit Web Application for LLM File System Assistant

Provides an interactive dashboard for document inspection, keyword search,
resume uploads, tool execution tracing, and real-time AI Agent chat.
"""

import os
import json
import sys
from pathlib import Path
import streamlit as st

# Setup sys.path so imports work seamlessly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import fs_tools
from src import llm_file_assistant

# Page Configuration
st.set_page_config(
    page_title="LLM File System Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    /* Dark glassmorphic theme styling */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .tool-badge {
        background: #312e81;
        color: #a5b4fc;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 8px;
    }
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        border-color: #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_history" not in st.session_state:
    st.session_state.tool_history = []

# Sidebar Controls & Information
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/artificial-intelligence.png", width=64)
    st.markdown("<h2 style='margin-top:0;'>LLM File Assistant</h2>", unsafe_allow_html=True)
    st.caption("Powered by LangChain & OpenAI / OpenRouter Tool Calling")
    st.divider()

    # Model Status Indicator
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if openrouter_key:
        st.success("🟢 Connected: OpenRouter API")
        st.caption(f"Model: `{os.environ.get('MODEL_NAME', 'openai/gpt-4o-mini')}`")
    elif openai_key:
        st.success("🟢 Connected: OpenAI API")
        st.caption(f"Model: `{os.environ.get('MODEL_NAME', 'gpt-4o-mini')}`")
    else:
        st.error("🔴 API Key Missing! Check .env file.")

    st.divider()

    # Workspace Statistics
    resumes_dir = Path("resumes")
    summaries_dir = Path("summaries")
    
    resume_files = list(resumes_dir.glob("*")) if resumes_dir.exists() else []
    summary_files = list(summaries_dir.glob("*")) if summaries_dir.exists() else []

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(resume_files)}</div><div class='metric-label'>Resumes</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(summary_files)}</div><div class='metric-label'>Reports</div></div>", unsafe_allow_html=True)

    st.divider()

    # Resume Upload Tool
    st.markdown("### 📤 Upload New Resume")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
    if uploaded_file is not None:
        resumes_dir.mkdir(exist_ok=True)
        save_path = resumes_dir / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.toast(f"Uploaded {uploaded_file.name} to resumes/", icon="✅")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_history = []
        st.rerun()

# Main Application Header
st.markdown("<div class='main-header'>🧠 Agentic File System Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Autonomous document inspection, RAG candidate matching, and tool execution workspace</div>", unsafe_allow_html=True)

# Tabs
tab_chat, tab_explorer, tab_search, tab_reports = st.tabs([
    "💬 Agent Chat", 
    "📂 Document Explorer", 
    "🔍 Keyword Context Search", 
    "💾 Generated Reports"
])

# =====================================================================
# TAB 1: AGENT CHAT INTERFACE
# =====================================================================
with tab_chat:
    st.markdown("### Quick Demo Benchmarks")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    preset_query = None
    if btn_col1.button("📑 Read All Resumes", use_container_width=True):
        preset_query = "Read all resumes in the resumes folder"
    if btn_col2.button("🐍 Find Python Experience", use_container_width=True):
        preset_query = "Find resumes mentioning Python experience"
    if btn_col3.button("📝 Summarize John Doe", use_container_width=True):
        preset_query = "Create a summary file for resumes/resume_john_doe.pdf at summaries/john_doe_summary.txt"

    st.divider()

    # Render Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "tools" in msg and msg["tools"]:
                with st.expander("🛠️ Tool Calls Executed", expanded=False):
                    for t in msg["tools"]:
                        st.markdown(f"<span class='tool-badge'>{t['tool']}</span>", unsafe_allow_html=True)
                        st.json(t["args"])
                        try:
                            st.json(json.loads(t["result"]))
                        except Exception:
                            st.text(t["result"])

    # Chat Input Box
    user_input = st.chat_input("Ask the assistant to inspect resumes, find skills, or generate reports...")
    active_query = preset_query or user_input

    if active_query:
        st.session_state.messages.append({"role": "user", "content": active_query})
        with st.chat_message("user"):
            st.markdown(active_query)

        with st.chat_message("assistant"):
            with st.spinner("🤖 LLM Agent selecting tools and processing query..."):
                try:
                    answer, tool_logs = llm_file_assistant.run_assistant_agent(active_query)
                    st.markdown(answer)
                    
                    if tool_logs:
                        with st.expander("🛠️ Tool Calls Executed", expanded=True):
                            for t in tool_logs:
                                st.markdown(f"<span class='tool-badge'>{t['tool']}</span>", unsafe_allow_html=True)
                                st.json(t["args"])
                                try:
                                    st.json(json.loads(t["result"]))
                                except Exception:
                                    st.text(t["result"])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "tools": tool_logs
                    })
                except Exception as e:
                    st.error(f"Error running agent: {e}")

# =====================================================================
# TAB 2: DOCUMENT EXPLORER & VIEWER
# =====================================================================
with tab_explorer:
    st.markdown("### 📂 Document Inspector")
    files_list = fs_tools.list_files("resumes")
    
    if files_list and "error" not in files_list[0]:
        selected_file_name = st.selectbox(
            "Select a resume file to inspect:",
            options=[f["name"] for f in files_list]
        )
        
        if selected_file_name:
            target_path = os.path.join("resumes", selected_file_name)
            doc_res = fs_tools.read_file(target_path)
            
            if doc_res.get("status") == "success":
                meta = doc_res["metadata"]
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("File Name", meta["name"])
                m_col2.metric("Size", f"{meta['size_bytes']} bytes")
                m_col3.metric("Type", meta["type"].upper())
                
                st.markdown("#### Document Text Content")
                st.code(doc_res["content"], language="text")
            else:
                st.error(doc_res.get("error"))
    else:
        st.warning("No files found in resumes/ directory.")

# =====================================================================
# TAB 3: KEYWORD CONTEXT SEARCH TOOL
# =====================================================================
with tab_search:
    st.markdown("### 🔍 Case-Insensitive Keyword Search")
    st.caption("Executes `fs_tools.search_in_file` across all resume documents with context snippets")
    
    search_keyword = st.text_input("Enter keyword (e.g. 'Python', 'Docker', 'AWS', 'Literature'):", value="Python")
    if st.button("Search Resumes"):
        search_res = fs_tools.search_in_file("resumes", search_keyword)
        if search_res.get("status") == "success":
            st.success(f"Found {search_res['matches_found']} matches for '{search_keyword}'")
            for m in search_res.get("matches", []):
                with st.expander(f"👤 Candidate: {m['person_name']} | Line {m['line_number']}: {m['match']}"):
                    st.caption(f"File: `{m['filepath']}`")
                    st.code(m["context"], language="text")
        else:
            st.error(search_res.get("error", "Search failed."))

# =====================================================================
# TAB 4: GENERATED REPORTS VIEW
# =====================================================================
with tab_reports:
    st.markdown("### 💾 Output Reports (`summaries/`)")
    if summaries_dir.exists():
        summary_files_list = list(summaries_dir.glob("*.txt"))
        if summary_files_list:
            selected_summary = st.selectbox(
                "Select a generated summary report:",
                options=[sf.name for sf in summary_files_list]
            )
            if selected_summary:
                sum_path = summaries_dir / selected_summary
                content = sum_path.read_text(encoding="utf-8", errors="ignore")
                st.markdown(f"#### Report: `{selected_summary}`")
                st.text_area("Report Content", content, height=350)
        else:
            st.info("No report files found in `summaries/` yet. Ask the AI Agent to generate one!")
    else:
        st.info("The `summaries/` directory does not exist yet. Run an agent query to create reports.")
