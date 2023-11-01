from typing import Optional, Any, Coroutine

from db import redis
from elastic_transport import ObjectApiResponse
from elasticsearch import BadRequestError, AsyncElasticsearch
from pydantic._internal._model_construction import ModelMetaclass


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

    def _get_object_from_elastic(self, object_id: str) -> Optional[model]:
        doc = self.elastic.get(index=self.index, id=object_id)
        return self.model(**doc['_source'])

    @staticmethod
    def _transform_to_dict_elastic_request(request: ObjectApiResponse, model: ModelMetaclass) -> list[model]:
        objects = request['hits']['hits']

        return [model(**fields['_source']) for fields in objects]


