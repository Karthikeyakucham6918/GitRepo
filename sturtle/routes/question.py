from fastapi import APIRouter, Request, Form
from urllib.parse import unquote

from sturtle.models.QuestionModel import QuestionModel
from sturtle.web import templates

router = APIRouter(tags=["Web"], prefix="/www/question")


@router.get("/debug")
async def index(request: Request):
    return templates.TemplateResponse("debug_question.html", {"request": request, "title": "Debug Question"})
