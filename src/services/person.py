from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, BadRequestError
from fastapi import Depends

from db.elastic import get_elastic
from models.pesron import Person
from services.base import BaseService


class PersonService(BaseService):
    model = Person
    index = 'person'

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            persons = self.elastic.search(index=self.index, body={
                "size": count,
                "from": offset,
            })
        except BadRequestError as e:
            print(e)
            return None

        if not persons:
            return None

        persons = self._transform_to_dict_elastic_request(persons, model=self.model)

        return persons

    async def search_by_query(self, query: str, fields: str, sort: str):
        query = {
            "multi_match": {
                "query": query,
                "fields": [field for field in fields.split(', ')]
            }
        }
        try:
            object = self.elastic.search(index=self.index, body={
                "query": query
            })
        except BadRequestError as e:
            print(e)
            return None

        if not object:
            return None

        objects = self._transform_to_dict_elastic_request(object, model=self.model)

        return objects


@lru_cache()
def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
