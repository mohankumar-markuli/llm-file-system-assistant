import os
import datetime
from pathlib import Path
from pypdf import PdfReader
import docx

def read_file(filepath: str) -> dict:
    """
    Read a file (PDF, TXT, DOCX) or all files in a directory and extract text content along with metadata.
    If filepath is a directory, reads all supported files in that directory at once.
    
    Args:
        filepath (str): Path to a single file or a directory containing files.
        
    Returns:
        dict: Structured response with status, content/documents, and metadata.
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return {"status": "failed", "error": f"File or directory not found: {filepath}"}

        # Handle directory reading (reads ALL supported files in directory)
        if path.is_dir():
            supported_exts = {'.pdf', '.txt', '.docx'}
            documents = []
            for item in sorted(path.iterdir()):
                if item.is_file() and item.suffix.lower() in supported_exts:
                    file_res = _read_single_file(item)
                    if file_res.get("status") == "success":
                        person_name = item.stem.replace("resume_", "").replace("_", " ").title()
                        lines = [line.strip() for line in file_res["content"].splitlines() if line.strip()]
                        if lines and "-" in lines[0]:
                            person_name = lines[0].split("-")[0].strip()

                        documents.append({
                            "person_name": person_name,
                            "filename": item.name,
                            "filepath": str(item),
                            "content": file_res["content"],
                            "metadata": file_res["metadata"]
                        })

            return {
                "status": "success",
                "directory": str(path),
                "files_read_count": len(documents),
                "documents": documents
            }

        # Handle single file reading
        if not path.is_file():
            return {"status": "failed", "error": f"Path is not a file or directory: {filepath}"}

        return _read_single_file(path)

    except Exception as e:
        return {"status": "failed", "error": str(e)}

def _read_single_file(path: Path) -> dict:
    """Internal helper to read and parse a single PDF, TXT, or DOCX file."""
    try:
        extension = path.suffix.lower()
        content = ""

        if extension == '.txt':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        elif extension == '.pdf':
            reader = PdfReader(str(path))
            extracted = [page.extract_text() for page in reader.pages if page.extract_text()]
            content = "\n".join(extracted)
        elif extension == '.docx':
            doc = docx.Document(str(path))
            content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        else:
            return {
                "status": "failed",
                "error": f"Unsupported file type: '{extension}'. Supported formats: .pdf, .txt, .docx"
            }

        stat = path.stat()
        mod_time = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        metadata = {
            "name": path.name,
            "filepath": str(path),
            "size_bytes": stat.st_size,
            "type": extension,
            "modified_date": mod_time
        }

        return {
            "status": "success",
            "content": content,
            "metadata": metadata
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}

def read_directory(directory: str, extension: str = None) -> dict:
    """Alias function for read_file when explicitly passing a directory path."""
    return read_file(directory)

def list_files(directory: str, extension: str = None) -> list:
    """
    List all files in a directory, optionally filtered by extension.
    
    Args:
        directory (str): Directory path to list files from.
        extension (str, optional): Extension filter (e.g. '.pdf', 'txt').
        
    Returns:
        list: List of metadata dicts for files found in directory.
    """
    try:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return [{"status": "failed", "error": f"Directory not found or invalid: {directory}"}]

        if extension:
            ext = extension.strip().lower()
            if not ext.startswith('.'):
                ext = f".{ext}"
        else:
            ext = None

        files = []
        for item in sorted(path.iterdir()):
            if item.is_file():
                if ext and item.suffix.lower() != ext:
                    continue
                stat = item.stat()
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size_bytes": stat.st_size,
                    "modified_date": mod_time,
                    "type": item.suffix.lower()
                })
        return files

    except Exception as e:
        return [{"status": "failed", "error": str(e)}]

def write_file(filepath: str, content: str) -> dict:
    """
    Write content to a file, creating any required parent directories.
    
    Args:
        filepath (str): Path of destination file.
        content (str): Text content to write.
        
    Returns:
        dict: Success or failure dictionary.
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        stat = path.stat()
        return {
            "status": "success",
            "message": f"Successfully written to {filepath}",
            "filepath": str(path),
            "size_bytes": stat.st_size
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def search_in_file(filepath: str, keyword: str) -> dict:
    """
    Search for a keyword in a file content (case-insensitive) and return matches with context.
    
    Args:
        filepath (str): Target file path.
        keyword (str): Search keyword.
        
    Returns:
        dict: Matches found, match count, keyword, and surrounding context.
    """
    try:
        read_result = read_file(filepath)
        if read_result.get("status") == "failed":
            return read_result

        # Handle directory-wide search result
        if "documents" in read_result:
            all_matches = []
            for doc in read_result["documents"]:
                lines = doc["content"].splitlines()
                keyword_lower = keyword.lower()
                for i, line in enumerate(lines):
                    if keyword_lower in line.lower():
                        start = max(0, i - 1)
                        end = min(len(lines), i + 2)
                        all_matches.append({
                            "person_name": doc["person_name"],
                            "filepath": doc["filepath"],
                            "line_number": i + 1,
                            "match": line.strip(),
                            "context": "\n".join(lines[start:end])
                        })
            return {
                "status": "success",
                "directory": filepath,
                "keyword": keyword,
                "matches_found": len(all_matches),
                "matches": all_matches
            }

        content = read_result.get("content", "")
        lines = content.splitlines()
        keyword_lower = keyword.lower()
        
        matches = []
        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context_lines = lines[start:end]
                matches.append({
                    "line_number": i + 1,
                    "match": line.strip(),
                    "context": "\n".join(context_lines)
                })

        return {
            "status": "success",
            "filepath": str(filepath),
            "keyword": keyword,
            "matches_found": len(matches),
            "matches": matches
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}
