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

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            genres = self.elastic.search(index=self.index, body={
                "size": count,
                "from": offset,
            })
        except BadRequestError as e:
            print(e)
            return None

        if not genres:
            return None

        genres = self._transform_to_dict_elastic_request(genres, model=self.model)

        return genres


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
