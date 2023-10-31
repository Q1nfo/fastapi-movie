import orjson

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class Writers(Person):
    pass


class Actors(Person):
    pass


class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float
    genre: list[str]
    writers: list[Writers]
    actors: list[Actors]
    actors_names: list[str]
    writers_names: list[str]
    director: list[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
