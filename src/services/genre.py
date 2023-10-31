from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, BadRequestError
from fastapi import Depends

from db.elastic import get_elastic
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    model = Genre
    index = 'genre'

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[model]:
        genre = await self._object_from_cache(genre_id)
        if not genre:
            genre = self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_object_to_cache(genre)

        return genre

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            genres = self.elastic.search(index=self.index, body={
                "size": count,
                "from": offset,
                # "sort": {
                #     sort: {
                #         "order": "desc",
                #     }
                # },
            })
        except BadRequestError as e:
            print(e)
            return None

        if not genres:
            return None

        genres = self._transform_to_dict_elastic_request(genres, model=self.model)

        return genres

    def _get_genre_from_elastic(self, genre_id: str) -> Optional[model]:
        doc = self.elastic.get(index='genre', id=genre_id)
        return self.model(**doc['_source'])


@lru_cache()
def get_genre_service(
        # redis: aioredis.Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
