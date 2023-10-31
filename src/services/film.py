from functools import lru_cache
from typing import Optional

from elastic_transport import ObjectApiResponse
from pydantic._internal._model_construction import ModelMetaclass
from redis import asyncio as aioredis
from elasticsearch import AsyncElasticsearch, BadRequestError
from fastapi import Depends

from db import redis
from db.elastic import get_elastic
from models.film import Film
from services.base import BaseService


class FilmService(BaseService):
    index = 'movies'
    model = Film
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[model]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            films = self.elastic.search(index=self.index, body={
                "size": count,
                "from": offset,
                "sort": {
                    sort: {
                        "order": "desc",
                    }
                },
            })
        except BadRequestError as e:
            print(e)
            return None

        if not films:
            return None

        films = self._transform_to_dict_elastic_request(films, model=self.model)

        return films

    def _get_film_from_elastic(self, film_id: str) -> Optional[model]:
        doc = self.elastic.get(index='movies', id=film_id)
        return self.model(**doc['_source'])


# class FilmService:
#     def __init__(self, redis: aioredis.Redis, elastic: AsyncElasticsearch):
#         self.redis = redis
#         self.elastic = elastic
#
#     async def get_by_id(self, film_id: str) -> Optional[Film]:
#         film = await self._film_from_cache(film_id)
#         if not film:
#             film = self._get_film_from_elastic(film_id)
#             if not film:
#                 return None
#             await self._put_film_to_cache(film)
#
#         return film
#
#     async def get_by_filters(self, count: int,
#                              offset: int,
#                              sort: str) -> Optional[list[Film]]:
#         try:
#             films = self.elastic.search(index='movies', body={
#                 "size": count,
#                 "from": offset,
#                 "sort": {
#                     sort: {
#                         "order": "desc"
#                     }
#                 },
#             })
#         except BadRequestError as e:
#             print(e)
#             return None
#
#         if not films:
#             return None
#
#         films = self._transform_to_dict_elastic_request(films, model=Film)
#
#         return films
#
#     async def _film_from_cache(self, film_id: str) -> Optional[Film]:
#         try:
#             async with self.redis.pipeline(transaction=True) as pipe:
#                 data = await pipe.get(film_id).execute()
#         except Exception as e:
#             return None
#         if not data:
#             return None
#
#     @staticmethod
#     def _transform_to_dict_elastic_request(request: ObjectApiResponse, model: ModelMetaclass) -> list[Film]:
#         objects = request['hits']['hits']
#
#         return [model(**fields['_source']) for fields in objects]
#
#     def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
#         doc = self.elastic.get(index='movies', id=film_id)
#         return Film(**doc['_source'])
#
#     async def _put_film_to_cache(self, film: Film):
#         try:
#             async with self.redis.pipeline(transaction=True) as pipe:
#                 await pipe.set(film.id, film.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)
#         except Exception as e:
#             print(e)


@lru_cache()
def get_film_service(
        # redis: aioredis.Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)

# @lru_cache()
# def get_film_service() -> FilmService:
#     return FilmService()
