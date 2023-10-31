from datetime import datetime

import orjson

from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
    description: str | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
