import ast
from pathlib import Path
from astchunk import ASTChunkBuilder

CHUNK_CONFIG = {
    "max_chunk_size": 1500,
    "language": "python",
    "metadata_template": "default",
}


def _get_line_numbers(source: str, symbol_name: str, fallback_line: int) -> tuple[int, int]:
    """
    Uses Python's built-in AST to find the exact start and end line of a function/class.
    """
    if not symbol_name:
        return fallback_line, fallback_line
    
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == symbol_name:
                    
                    return node.lineno, node.end_lineno
    except Exception:
        pass
        
    return fallback_line, fallback_line


def parse_file(file_path: str, repo_root: str) -> list[dict]:
    full_path = Path(repo_root) / file_path
    if not full_path.exists():
        return []

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    if not source.strip():
        return []

    configs = {**CHUNK_CONFIG, "repo_level_metadata": {"filepath": file_path}}
    builder = ASTChunkBuilder(**configs)

    try:
        raw_chunks = builder.chunkify(source)
    except Exception:
        return []

    chunks = []
    for c in raw_chunks:
        raw_content = c.get("content", "").strip()
        if not raw_content:
            continue

        meta = c.get("metadata", {})
        symbol_name = meta.get("name", "")
        symbol_type = meta.get("type", "")
        
        
        if not symbol_name and raw_content.startswith("def "):
            symbol_name = raw_content.split("def ")[1].split("(")[0].strip()
            symbol_type = "function"
        elif not symbol_name and raw_content.startswith("class "):
            symbol_name = raw_content.split("class ")[1].split(":")[0].split("(")[0].strip()
            symbol_type = "class"

        
        start_line, end_line = _get_line_numbers(source, symbol_name, fallback_line=1)

        chunks.append({
            "file_path": file_path,
            "symbol_name": symbol_name,
            "symbol_type": symbol_type,
            "line_start": start_line,
            "line_end": end_line,
            "content": raw_content,
        })

    return chunks