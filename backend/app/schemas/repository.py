from pydantic import BaseModel


class RepositoryCreateRequest(BaseModel):
    url: str


class RepositoryFileResponse(BaseModel):
    path: str
    size_bytes: int

    model_config = {"from_attributes": True}


class RepositoryResponse(BaseModel):
    id: int
    url: str
    status: str
    file_count: int
    local_path: str | None = None

    model_config = {"from_attributes": True}