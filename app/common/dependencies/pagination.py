from dataclasses import dataclass

from fastapi import Query


@dataclass
class PaginationParams:
    skip: int = 0
    limit: int = 100


def common_pagination(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)
