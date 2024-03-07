import os

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles


def get_dir(subdir=None):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), subdir) if subdir else os.path.dirname(
        os.path.realpath(__file__))


templates = Jinja2Templates(directory=get_dir("templates"))

static_files = StaticFiles(directory=get_dir("static"))
