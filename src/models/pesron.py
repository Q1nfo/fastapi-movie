from datetime import datetime

import orjson

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    full_name: str
    birth_date: datetime | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
