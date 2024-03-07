from dotenv import load_dotenv
from fastapi import FastAPI

from sturtle.routes import index_router
from sturtle.routes import question_router
from sturtle.routes import survey_router
from sturtle.routes import thread_router
from sturtle.web.routes import router as web_router
from sturtle.web import static_files
from sturtle.db import Base, engine

load_dotenv()
#test
app = FastAPI()

app.mount("/static", static_files, name="static")
app.include_router(index_router)
app.include_router(question_router)
app.include_router(survey_router)
app.include_router(thread_router)
app.include_router(web_router)

Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    # use LOGGING_CONFIG to configure logging


    uvicorn.run(app, host="0.0.0.0", port=8000)
