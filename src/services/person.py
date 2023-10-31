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

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[model]:
        person = await self._object_from_cache(person_id)
        if not person:
            person = self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_object_to_cache(person)

        return person

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            persons = self.elastic.search(index=self.index, body={
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

        if not persons:
            return None

        persons = self._transform_to_dict_elastic_request(persons, model=self.model)

        return persons

    def _get_person_from_elastic(self, person_id: str) -> Optional[model]:
        doc = self.elastic.get(index='person', id=person_id)
        return self.model(**doc['_source'])


@lru_cache()
def get_person_service(
        # redis: aioredis.Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
