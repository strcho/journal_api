from fastapi import APIRouter, Depends

from app.api.deps_v2 import get_mongo_store_dep
from app.schemas.journal import (
    JournalListResponse,
    CreateJournalRequest,
    UpdateJournalRequest,
    Journal,
)
from app.schemas.errors import ErrorResponse
from app.services.journal_v2 import JournalService
from app.database.mongo import MongoStore


def get_journal_service(
    store: MongoStore = Depends(get_mongo_store_dep),
) -> JournalService:
    return JournalService(store)


router = APIRouter(prefix="/journals", tags=["journals"])


@router.get(
    "",
    response_model=JournalListResponse,
    responses={401: {"model": ErrorResponse}},
)
async def list_journals(journal_service: JournalService = Depends(get_journal_service)):
    journals = await journal_service.list_journals()
    return JournalListResponse(journals=journals)


@router.post(
    "",
    response_model=Journal,
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def create_journal(
    payload: CreateJournalRequest,
    journal_service: JournalService = Depends(get_journal_service),
):
    return await journal_service.create_journal(payload)


@router.put(
    "/{journal_id}",
    response_model=Journal,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def update_journal(
    journal_id: str,
    payload: UpdateJournalRequest,
    journal_service: JournalService = Depends(get_journal_service),
):
    return await journal_service.update_journal(journal_id, payload)


@router.delete(
    "/{journal_id}",
    responses={
        204: {"model": None},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def delete_journal(
    journal_id: str,
    journal_service: JournalService = Depends(get_journal_service),
):
    await journal_service.delete_journal(journal_id)
