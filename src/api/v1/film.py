from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float
    genre: list[str]
    writers: list[Any]
    actors: list[Any]
    actors_names: list[str]
    writers_names: list[str]
    director: list[str]


@router.get('/movies/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(**film.dict())


@router.get('/movies')
async def film_list(film_service: FilmService = Depends(get_film_service),
                    count: int = 10, offset: int = 0,
                    sort: Optional[str] = "id") -> list[Film]:

    films = await film_service.get_by_filters(count, offset, sort)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found in cinema')

    response = [Film(**film.dict()) for film in films]

    return response
