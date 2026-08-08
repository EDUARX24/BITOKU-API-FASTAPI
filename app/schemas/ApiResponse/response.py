from typing import Any, List, Optional
from pydantic import BaseModel, Field

class ApiResponse(BaseModel):
    statusCode: int
    isSuccess: bool
    errorMessages: Optional[List[str]] = Field(default_factory=list)
    successMessages: Optional[List[str]] = Field(default_factory=list)
    result: Optional[Any] = None
