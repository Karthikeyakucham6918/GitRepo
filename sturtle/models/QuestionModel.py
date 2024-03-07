from typing import Optional
from pydantic import BaseModel


class QuestionModel(BaseModel):
    question_id: str
    thread_id: str
    name: str
    text: str
    options: Optional[list[str]] = None
    response: Optional[int] = None
    response_text: Optional[str] = None


"""
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "survey_id": {
            "type": "string"
        },
        "question_id": {
            "type": "string"
        },
        "thread_id": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "text": {
            "type": "string"
        },
        "options": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "response": {
            "type": "string"
        },
        "response_text": {
            "type": "string"
        },
        "remarks": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
    },
    "required": ["survey_id", "question_id", "thread_id", "name", "text", "options"]
}
"""

"""
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "message": {
            "type": "string"
        },
        "options": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["message", "options"]
}
"""