import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from app.config import load_config, AppConfig
from app.database import get_emails, get_email_by_id, mark_as_read, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

security = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config("config.json")
    app.state.config = config
    init_db(config.db_path)
    logger.info("Web 服务启动: http://127.0.0.1:8000")
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def auth(credentials: HTTPBasicCredentials = Depends(security)):
    config: AppConfig = app.state.config
    is_correct_user = secrets.compare_digest(credentials.username, config.basic_auth_user)
    is_correct_pass = secrets.compare_digest(credentials.password, config.basic_auth_password)
    if not (is_correct_user and is_correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.get("/")
async def index(request: Request, _=Depends(auth)):
    emails = get_emails(app.state.config.db_path)
    return templates.TemplateResponse(request, "index.html", {"emails": emails})


@app.get("/mail/{email_id}")
async def detail(request: Request, email_id: int, _=Depends(auth)):
    email = get_email_by_id(app.state.config.db_path, email_id)
    if not email:
        return HTMLResponse("邮件不存在", status_code=404)
    mark_as_read(app.state.config.db_path, email_id)
    return templates.TemplateResponse(request, "detail.html", {"email": email})
