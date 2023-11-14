from datetime import datetime
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str
    birth_date: datetime | None


@router.get('/person/{person_id}',
            response_model=Person,
            summary='Поиск персоны',
            description='Поиск персоны по его id',
            response_description='Персона и ее параметры',
            )
@cache(expire=200)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(**person.dict())


@router.get('/persons',
            response_model=list[Person],
            summary='Поиск персон',
            description='Поиск персон по фильтрам',
            response_description='Список персон их параметры',
            )
@cache(expire=200)
async def film_list(person_service: PersonService = Depends(get_person_service),
                    count: int = 10, offset: int = 0,
                    sort: Optional[str] = "id") -> list[Person]:

    persons = await person_service.get_by_filters(count, offset, sort)

    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found in cinema')

    response = [Person(**person.dict()) for person in persons]

    return response


@router.get('/genres/search/',
            response_model=list[Person],
            summary='Поиск персон',
            description='Полнотекстовый поиск персон',
            response_description='Список персон подходящих под критерии поиска',
            )
async def film_search(person_service: PersonService = Depends(get_person_service), query: str = '', sort: str = 'id',
                      fields: str = 'name'):

    persons = await person_service.search_by_query(query, fields, sort)

    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found in your fields')

    response = [Person(**genre.dict()) for genre in [persons]]

    return response
