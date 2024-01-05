"""
qualtrix rest api
"""

import logging

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel, typing

from qualtrix import client, error

log = logging.getLogger(__name__)

router = fastapi.APIRouter()


class SurveyModel(BaseModel):
    surveyId: str


class ResponseModel(SurveyModel):
    responseId: str


class SessionModel(SurveyModel):
    sessionId: str


class RedirectModel(SurveyModel):
    directoryId: str
    targetSurveyId: str
    responseId: str


@router.post("/bulk-responses")
async def get_bulk_responses(request: SurveyModel):
    return client.result_export(request.surveyId)


@router.post("/response")
async def get_response(request: ResponseModel):
    try:
        return client.get_response(request.surveyId, request.responseId)
    except error.QualtricsError as e:
        raise HTTPException(status_code=400, detail=e.args)


@router.post("/redirect")
async def get_redirect(request: RedirectModel):
    try:
        email = client.get_email(request.surveyId, request.responseId)
        contact = client.get_contact(request.directoryId, email)
        distribution = client.get_distribution(request.directoryId, contact["id"])
        return client.get_link(request.targetSurveyId, distribution["distributionId"])
    except error.QualtricsError as e:
        raise HTTPException(status_code=400, detail=e.args)


@router.post("/survey-schema")
async def get_schema(request: SurveyModel):
    return client.get_survey_schema(request.surveyId)


@router.post("/delete-session")
async def session(request: SessionModel):
    """
    Router for ending a session, pulling response
    """
    try:
        return client.delete_session(request.surveyId, request.sessionId)
    except error.QualtricsError as e:
        raise HTTPException(status_code=400, detail=e.args)
