from dataclasses import dataclass

from fastapi import Query


@dataclass
class PaginationParams:
    skip: int = 0
    limit: int = 100


def common_pagination(
    skip: int = Query(default=None, ge=0),
    limit: int = Query(default=None, ge=1, le=5000),
    page: int = Query(default=None, ge=1),
    per_page: int = Query(default=None, ge=1, le=5000),
) -> PaginationParams:
    final_limit = limit if limit is not None else (per_page if per_page is not None else 100)
    
    if skip is not None:
        final_skip = skip
    else:
        final_page = page if page is not None else 1
        final_skip = (final_page - 1) * final_limit

    return PaginationParams(skip=final_skip, limit=final_limit)
