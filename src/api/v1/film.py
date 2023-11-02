from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
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


@router.get('/movies/{film_id}',
            response_model=Film,
            summary='Поиск кинопроизведения',
            description='Поиск кинопроизведения по его id',
            response_description='Название и рейтинг фильма',
            )
@cache(expire=200)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(**film.dict())


@router.get('/movies')
@cache(expire=200)
async def film_list(film_service: FilmService = Depends(get_film_service),
                    count: int = 10, offset: int = 0,
                    sort: Optional[str] = "id") -> list[Film]:
    films = await film_service.get_by_filters(count, offset, sort)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found in cinema')

    response = [Film(**film.dict()) for film in films]

    return response


@router.get('/movies/search/')
async def film_search(film_service: FilmService = Depends(get_film_service), query: str = '', sort: str = 'id',
                      fields: str = 'title, description'):
    films = await film_service.search_by_query(query, fields, sort)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found in your fields')

    response = [Film(**film.dict()) for film in films]

    return response
