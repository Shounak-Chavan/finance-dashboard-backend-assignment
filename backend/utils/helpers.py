from typing import Optional


# 🔥 Pagination helper
def get_pagination(page: int = 1, limit: int = 10) -> tuple[int, int]:
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    offset = (page - 1) * limit
    return offset, limit


# 🔥 Safe update helper (used in services)
def update_model_fields(instance, data: dict):
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)
    return instance


# 🔥 Standard response formatter (optional)
def success_response(
    data: Optional[dict] = None,
    message: str = "Success"
):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str = "Something went wrong"
):
    return {
        "success": False,
        "message": message
    }