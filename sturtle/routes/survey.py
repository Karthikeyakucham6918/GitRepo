from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sturtle.models.SurveyModel import SurveyModel
from sturtle.db import get_db
from sturtle.db.models import Survey, Thread

router = APIRouter(tags=["API", "Survey"], prefix="/api/v1")

@router.get("/surveys")
async def get_surveys(db: Session = Depends(get_db)):
    db_surveys = db.query(Survey).all()
    return {"surveys": db_surveys}


@router.post("/survey")
async def create_survey(survey: SurveyModel, db: Session = Depends(get_db)):

    db_survey = Survey(
        name=survey.name,
        description=survey.description,
        prompt=survey.prompt
    )

    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return {"message": "Survey created successfully", "id": db_survey.id}

@router.put("/survey/{survey_id}")
async def update_survey(survey_id: str, survey: SurveyModel, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    db_survey.name = survey.name
    db_survey.description = survey.description
    db_survey.prompt = survey.prompt

    db.commit()
    db.refresh(db_survey)

    return {"message": "Survey updated successfully", "survey": db_survey}

@router.get("/survey/{survey_id}")
async def get_survey(survey_id: str, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    return {"survey": db_survey}


@router.delete("/survey/{survey_id}")
async def delete_survey(survey_id: str, db: Session = Depends(get_db)):
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    db.delete(db_survey)
    db.commit()

    return {"message": "Survey deleted successfully"}

