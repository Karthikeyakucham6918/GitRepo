from typing import List
from pydantic import BaseModel


class SurveyModel(BaseModel):
    name: str
    description: str
    prompt: str

    files: List[str]
