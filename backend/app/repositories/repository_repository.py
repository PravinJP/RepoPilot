from sqlalchemy.orm import Session

from app.models.repository import Repository, RepositoryFile


class RepositoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, url: str) -> Repository:
        repo = Repository(url=url, status="pending")
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def update_status(
        self,
        repo_id: int,
        status: str,
        file_count: int | None = None,
        local_path: str | None = None,
    ) -> Repository:
        repo = self.db.get(Repository, repo_id)
        if repo is None:
            raise ValueError(f"Repository {repo_id} not found")
        repo.status = status
        if file_count is not None:
            repo.file_count = file_count
        if local_path is not None:
            repo.local_path = local_path
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def add_files(self, repo_id: int, files: list[dict]) -> int:
        rows = [
            RepositoryFile(
                repository_id=repo_id,
                path=f["path"],
                size_bytes=f["size_bytes"],
            )
            for f in files
        ]
        self.db.add_all(rows)
        self.db.commit()
        return len(rows)

    def get_by_id(self, repo_id: int) -> Repository | None:
        return self.db.get(Repository, repo_id)