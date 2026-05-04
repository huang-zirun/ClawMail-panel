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
from app.captcha import extract_captcha

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


def _enrich_captcha(email: dict) -> dict:
    for field in ("subject", "text_body", "html_body"):
        val = email.get(field)
        if val:
            captcha = extract_captcha(val)
            if captcha:
                email["captcha"] = captcha
                return email
    email["captcha"] = None
    return email


@app.get("/")
async def index(request: Request, _=Depends(auth)):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/api/emails")
async def api_emails(_=Depends(auth)):
    emails = get_emails(app.state.config.db_path)
    return [_enrich_captcha(e) for e in emails]


@app.get("/api/emails/{email_id}")
async def api_email_detail(email_id: int, _=Depends(auth)):
    email = get_email_by_id(app.state.config.db_path, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    return _enrich_captcha(email)


@app.post("/api/emails/{email_id}/read")
async def api_email_read(email_id: int, _=Depends(auth)):
    mark_as_read(app.state.config.db_path, email_id)
    return {"ok": True}


@app.get("/mail/{email_id}")
async def detail(request: Request, email_id: int, _=Depends(auth)):
    email = get_email_by_id(app.state.config.db_path, email_id)
    if not email:
        return HTMLResponse("邮件不存在", status_code=404)
    mark_as_read(app.state.config.db_path, email_id)
    return templates.TemplateResponse(request, "detail.html", {"email": email})
