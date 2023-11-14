from typing import Optional, Any, Coroutine

from elastic_transport import ObjectApiResponse
from elasticsearch import BadRequestError, AsyncElasticsearch
from pydantic._internal._model_construction import ModelMetaclass

from db import redis


class BaseService:
    index = None
    redis = redis.redis
    model = None
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, object_id: str) -> Optional[model]:
        object = self._get_object_from_elastic(object_id)
        if not object:
            return None

        return object

    async def get_by_filters(self, count: int,
                             offset: int,
                             sort: str) -> Optional[list[model]]:
        try:
            object: Coroutine[Any, Any, ObjectApiResponse[Any]] = self.elastic.search(index=self.index, body={
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

        if not object:
            return None

        objects = self._transform_to_dict_elastic_request(object, model=self.model)

        return objects

    async def search_by_query(self, query: str, fields: str, sort: str):
        query = {
            "multi_match": {
                "query": query,
                "fields": [field for field in fields.split(', ')]
            }
        }
        sort = self._create_sort_query(sort)

        try:
            object: Coroutine[Any, Any, ObjectApiResponse[Any]] = self.elastic.search(index=self.index, body={
                "sort": sort,
                "query": query
            })
        except BadRequestError as e:
            print(e)
            return None

        if not object:
            return None

        objects = self._transform_to_dict_elastic_request(object, model=self.model)

        return objects

    def _get_object_from_elastic(self, object_id: str) -> Optional[model]:
        doc = self.elastic.get(index=self.index, id=object_id)
        return self.model(**doc['_source'])

    @staticmethod
    def _create_sort_query(sort_field: str) -> dict:
        if sort_field[0] == "-":
            return {sort_field[1:]: {"order": 'asc'}}
        return {sort_field: {'order': 'desc'}}

    @staticmethod
    def _transform_to_dict_elastic_request(request: ObjectApiResponse, model: ModelMetaclass) -> list[model]:
        objects = request['hits']['hits']

        return [model(**fields['_source']) for fields in objects]
