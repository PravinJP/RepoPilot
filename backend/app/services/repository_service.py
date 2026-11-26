import shutil
from pathlib import Path

from git import Repo as GitRepo
from sqlalchemy.orm import Session

from app.ai.ingestion import walk_python_files
from app.ai.parser import parse_file
from app.models.code_chunk import CodeChunk
from app.repositories.repository_repository import RepositoryRepository

CLONE_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "repos"

class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo_repo = RepositoryRepository(db)

    def ingest_from_url(self, url: str) -> dict:
        if "github.com" not in url:
            raise ValueError("Only GitHub URLs are supported")

        repo_record = self.repo_repo.create(url)

        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        local_path = CLONE_BASE_DIR / f"{repo_record.id}_{repo_name}"

        try:
            if local_path.exists():
                shutil.rmtree(local_path)

            CLONE_BASE_DIR.mkdir(parents=True, exist_ok=True)
            GitRepo.clone_from(url, str(local_path), depth=1)

            files = walk_python_files(str(local_path))
            if not files:
                raise ValueError("No Python files found in repository")

            self.repo_repo.add_files(repo_record.id, files)

            all_chunks = []
            for file_info in files:
                chunks = parse_file(file_info["path"], str(local_path))
                for chunk in chunks:
                    chunk["repository_id"] = repo_record.id
                    all_chunks.append(chunk)

            if all_chunks:
                self.db.add_all([CodeChunk(**c) for c in all_chunks])
                self.db.commit()

            updated = self.repo_repo.update_status(
                repo_record.id,
                status="ready",
                file_count=len(files),
                local_path=str(local_path),
            )

            return {
                "id": updated.id,
                "url": updated.url,
                "status": updated.status,
                "file_count": updated.file_count,
                "local_path": updated.local_path,
            }

        except Exception as e:
            self.repo_repo.update_status(repo_record.id, status="failed")
            if local_path.exists():
                try:
                    shutil.rmtree(local_path)
                except PermissionError:
                    pass
            raise RuntimeError(f"Ingestion failed: {e}") from e