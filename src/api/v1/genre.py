from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str
    description: str | None


@router.get('/genre/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(**genre.dict())


@router.get('/genres')
async def genre_list(genre_service: GenreService = Depends(get_genre_service),
                     count: int = 10, offset: int = 0,
                     sort: Optional[str] = "id") -> list[Genre]:
    genres = await genre_service.get_by_filters(count, offset, sort)

    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found in cinema')

    response = [Genre(**genre.dict()) for genre in genres]

    return response
