from typing import Any, List, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    statusCode: int
    isSuccess: bool
    errorMessages: Optional[List[str]] = []
    successMessages: Optional[List[str]] = []
    result: Optional[Any] = None