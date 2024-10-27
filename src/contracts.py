from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class ItemRequest(BaseModel):
    name: str
    price: float


class PatchItemRequest(BaseModel):
    name: str = None
    price: Annotated[float, Field(gt=0.0)] = None
    model_config = ConfigDict(extra="forbid")
