from typing import Optional

from db import redis
from elastic_transport import ObjectApiResponse
from elasticsearch import BadRequestError
from pydantic._internal._model_construction import ModelMetaclass


class BaseService:
    index = None
    redis = redis.redis
    model = None
    FILM_CACHE_EXPIRE_IN_SECONDS = None

    @classmethod
    async def _object_from_cache(cls, film_id: str) -> Optional[model]:
        try:
            async with cls.redis.pipeline(transaction=True) as pipe:
                data = await pipe.get(film_id).execute()
        except Exception as e:
            return None
        if not data:
            return None

    @staticmethod
    def _transform_to_dict_elastic_request(request: ObjectApiResponse, model: ModelMetaclass) -> list[model]:
        objects = request['hits']['hits']

        return [model(**fields['_source']) for fields in objects]

    @classmethod
    async def _put_object_to_cache(cls, index: model):
        try:
            async with cls.redis.pipeline(transaction=True) as pipe:
                await pipe.set(index.id, index.json(), ex=cls.FILM_CACHE_EXPIRE_IN_SECONDS)
        except Exception as e:
            print(e)

