import asyncio
import json
import re
from itertools import groupby
from traceback import print_exc

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from openai import OpenAI
from openai.types.beta.threads import Run
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sturtle.config import OPENAI_STURTLE_ASSISTANT_ID
from sturtle.db import get_db
from sturtle.db.models import Survey

load_dotenv()
client = OpenAI(api_key = "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")

router = APIRouter(tags=["API", "Thread"], prefix="/api/v1")


class CreateThreadRequestModel(BaseModel):
    survey_id: str


@router.get("/thread/test/{filename}")
async def test_thread(filename: str):

    class DebugText(BaseModel):
        value: str
    class DebugContent(BaseModel):
        text: DebugText
    class DebugThreadMessage(BaseModel):
        thread_id: str
        content: list[DebugContent]

    with open(f"./temp/{filename}") as f:
        s = json.load(f)

        model = [DebugThreadMessage(**i) for i in s]
        messages = unpack_messages(model)

    return messages


# Create a new thread from a survey
@router.post("/thread")
async def create_thread(model: CreateThreadRequestModel, db: Session = Depends(get_db)):
    survey_id = model.survey_id

    # Fetch the survey from the database
    db_survey = db.query(Survey).filter(Survey.id == survey_id).first()

    message = db_survey.prompt

    run = client.beta.threads.create_and_run(
        assistant_id=OPENAI_STURTLE_ASSISTANT_ID,
        thread={
            "messages": [
                {"role": "user", "content": message}
            ]
        }
    )

    messages = await read_async_messages(run)

    return unpack_messages(messages)

    # Create the thread in the database
    # db_thread = Thread(
    #     id=run.thread_id,
    #     survey_id=survey_id
    # )
    #
    # db.add(db_thread)
    # db.commit()
    # db.refresh(db_thread)
    # return {"message": "Thread created successfully", "id": db_thread.id}


async def read_async_messages(run: Run):
    thread_id = run.thread_id
    run_id = run.id
    print(run)
    while run.status not in ["completed", "failed", "cancelled", "expired"]:
        await asyncio.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        print(run)

    messages = []

    run_steps = client.beta.threads.runs.steps.list(
        thread_id=run.thread_id,
        run_id=run.id
    )

    for step in run_steps.data:
        if step.type == "message_creation":
            message_id = step.step_details.message_creation.message_id
            message = client.beta.threads.messages.retrieve(
                thread_id=thread_id,
                message_id=message_id
            )
            messages.append(message)

    return messages



def parse_blockquotes_from_string(s):
    messages = []

    def line_is_md(line):
        return bool(re.match(r'^(>|\d+\.|###|-|\*)', line))

    def find_last_question_element(array):
        return next((element for element in reversed(array) if element.get('type') in ['question', 'response']), None)

    chunks = [[item for item in group] for (key, group) in groupby(s.splitlines(), line_is_md)]
    for chunk in chunks:
        if line_is_md(chunk[0]):
            for line in chunk:
                if line.startswith('> '):
                    line = line[2:].strip()
                else:
                    line = line.strip()

                # If the line is an H3, it's a question
                if line.startswith('###'):
                    text = line[4:]
                    obj = {
                        "type": "question",
                        "options": []
                    }
                    # Parse the question ID from the text. Id is {#id}
                    matches = re.match(r'^(.*)\s*{#(.*)}\s*$', text)
                    if matches:
                        text = matches.group(1)
                        obj["id"] = matches.group(2)

                    obj["question"] = text
                    messages.append(obj)
                elif line.startswith('-'):
                    obj = find_last_question_element(messages)
                    if obj is None:
                        obj = {
                            "type": "response"
                        }
                        messages.append(obj)

                    # Parse response, response_text, remarks.
                    # These fields begin with - (response:|response_text:|**remarks:**)
                    matches = re.match(r'^-\s*(response:|response_text:|\*\*remarks:\*\*)\s*(.*)$', line)
                    if matches:
                        key = matches.group(1)
                        value = matches.group(2)
                        if key == 'response:':
                            obj["type"] = "response"
                            obj["response"] = value
                        elif key == 'response_text:':
                            obj["type"] = "response"
                            obj["response_text"] = value
                        elif key == '**remarks:**':
                            obj["remarks"] = value

                # If the line is wrapped in asterisks, it's instructions
                elif line.startswith('*') and line.endswith('*'):
                    obj = {
                        "type": "instruction",
                        "message": line[1:-1],
                    }
                    messages.append(obj)
                # If the line starts with a number, it's an option
                else:
                    obj = find_last_question_element(messages)
                    matches = re.match(r'^\d+\.\s?(.*)', line)
                    if matches:
                        obj["options"].append(matches.group(1))

        elif not "\n".join(chunk).strip():
            pass
        else:
            obj = {
                "type": "message",
                "message": "\n".join(chunk),
            }
            messages.append(obj)
    return messages


def coalesce_responses(response_obj):
    messages = groupby(response_obj['messages'], lambda x: x['type'])
    c_messages = []
    for key, group in messages:
        objs = [i for i in group]
        if key == 'response':
            response_list = {
                "type": "response_list",
                "responses": objs
            }

            if objs[0].get('question'):
                c_messages.append(response_list)
        else:
            c_messages.extend(objs)

    response_obj['messages'] = c_messages
    return response_obj


def unpack_messages(messages):
    response_obj = {
        "messages": [],
    }

    print(messages)

    for thread_message in messages:
        message_text = thread_message.content[0].text.value
        if thread_message.thread_id and 'thread_id' not in response_obj:
            response_obj["thread_id"] = thread_message.thread_id

        response_obj['messages'].extend(parse_blockquotes_from_string(message_text))

    response_obj = coalesce_responses(response_obj)

    return response_obj


class AppendMessageRequestModel(BaseModel):
    thread_id: str
    message: str


@router.post("/thread/{thread_id}/message")
async def append_message(model: AppendMessageRequestModel, db: Session = Depends(get_db)):
    thread_id = model.thread_id
    message = model.message

    if thread_id.startswith("debug"):
        return {
            "messages": []
        }

    print("Appending message to thread", thread_id, message)

    # # Fetch the thread from the database
    # db_thread = db.query(Thread).filter(Thread.id == thread_id).first()
    #
    # if db_thread is None:
    #     raise HTTPException(status_code=404, detail="Thread not found")

    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message,
    )
    print(thread_message)

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=OPENAI_STURTLE_ASSISTANT_ID,
    )

    messages = await read_async_messages(run)

    return unpack_messages(messages)
