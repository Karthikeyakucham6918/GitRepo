from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from sturtle.web import templates

router = APIRouter(tags=["Web"])


@router.get("/")
async def index(request: Request):
    return RedirectResponse(url='/www/surveys')
    # return templates.TemplateResponse("home.html", {"request": request, "title": "Home"})
