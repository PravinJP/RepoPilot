from pathlib import Path

SKIP_DIRS = {".git", "venv", ".venv", "__pycache__", "node_modules", ".tox", "build", "dist"}


def walk_python_files(repo_path: str) -> list[dict]:
    repo = Path(repo_path)
    if not repo.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    files = []
    for path in repo.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append({
            "path": str(path.relative_to(repo)),
            "size_bytes": path.stat().st_size,
        })

    return files