from fastapi import APIRouter, Depends, HTTPException, Request, Form
from urllib.parse import unquote
from sqlalchemy.orm import Session

from ..models.QuestionModel import QuestionModel

from ..db import get_db
from ..db.models import Survey, Thread
from ..web import templates

router = APIRouter(tags=["Web"], prefix="/www")

@router.get("/surveys")
async def view_surveys(request: Request, db: Session = Depends(get_db)):
    db_surveys = db.query(Survey).all()

    return templates.TemplateResponse("surveys.html", {"request": request, "surveys": db_surveys})

@router.get("/survey/create")
async def view_create_survey(request: Request):
    return templates.TemplateResponse("create_survey.html", {"request": request})

@router.get("/survey/{survey_id}/edit")
async def view_edit_survey(survey_id: str, request: Request, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    return templates.TemplateResponse("create_survey.html", {"request": request, "survey": db_survey})

@router.get("/survey/{survey_id}")
async def view_take_survey(survey_id: str, request: Request, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    return templates.TemplateResponse("thread.html", {"request": request, "survey": db_survey, "survey_id": survey_id})


@router.post("/render_question")
async def render_question(request: Request,
                          survey_id: str = Form(None),
                          question_id: str = Form(None),
                          thread_id: str = Form(None),
                          chat_message: str = Form(None),
                          name: str = Form(...),
                          text: str = Form(...),
                          options: str = Form(None)):
    # Split the options string into a list and decodeURIComponent
    options = options or ''
    options_list = [unquote(option) for option in (options.split(',')) if option]

    # Create a QuestionModel instance from the form data
    question = QuestionModel(survey_id=survey_id or '',
                             question_id=question_id or '',
                             thread_id=thread_id or '',
                             name=name,
                             text=text,
                             options=options_list)

    return templates.TemplateResponse("question.html", {
        "request": request,
        "question": question.model_dump(),
        "chat_message": chat_message
    })
