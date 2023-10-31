import logging

import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch, Elasticsearch
from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film
from api.v1 import person as person_router
from api.v1 import genre as genre_router
from core import config
from core.logger import LOGGING
from db import elastic
from db import redis
from db.indexies_from_elastic import Indexes
from services.elastic import IndexBuilder, Indexer

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = aioredis.ConnectionPool.from_url(f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}')
    # elastic.es = AsyncElasticsearch(hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    elastic.es = Elasticsearch(hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])

    genre_index = IndexBuilder(index_name='genre', model_from_postgres='"content".genre',
                               fields=['id', 'name', 'description'])
    genre = Indexer(elastic.es, genre_index, body=Indexes.genre.value)
    genre.complete_index()

    person_index = IndexBuilder(index_name='person', model_from_postgres='"content".person',
                                fields=['id', 'full_name', 'birth_date'])
    person = Indexer(elastic.es, person_index, body=Indexes.person.value)
    person.complete_index()


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(film.router, prefix='/v1/film', tags=['film'])
app.include_router(person_router.router, prefix='/v1/person', tags=['person'])
app.include_router(genre_router.router, prefix='/v1/genre', tags=['genre'])

if __name__ == '__main__':
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
