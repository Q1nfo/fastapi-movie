from functools import lru_cache

from elasticsearch import AsyncElasticsearch, BadRequestError
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from services.base import BaseService


class FilmService(BaseService):
    index = 'movies'
    model = Film
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@lru_cache()
def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)

