from datetime import datetime
from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str
    birth_date: datetime | None


@router.get('/person/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(**person.dict())


@router.get('/persons')
async def film_list(person_service: PersonService = Depends(get_person_service),
                    count: int = 10, offset: int = 0,
                    sort: Optional[str] = "id") -> list[Person]:
    persons = await person_service.get_by_filters(count, offset, sort)

    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found in cinema')

    response = [Person(**person.dict()) for person in persons]

    return response
