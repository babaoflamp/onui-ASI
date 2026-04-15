"""
공통 유틸리티
"""
from fastapi import Request


def _get_state(request: Request, name: str):
    """request.app.state에서 값을 가져온다. 없으면 None 반환."""
    return getattr(request.app.state, name, None)
