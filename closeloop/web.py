from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from starlette.middleware.sessions import SessionMiddleware

import closeloop.db as db_module
from closeloop.config import get_settings
from closeloop.db import get_db, init_db
from closeloop.marketing import (
    ADVANTAGES,
    CATALOGUE_PAGES,
    FLYER_BLURB,
    SOCIAL_POSTERS,
    STEP_BY_STEP_REGISTER,
)
from closeloop.models import Business, Estimate, FollowUp
from closeloop.seed import seed_demo
from closeloop.service import (
    authenticate_business,
    create_business,
    create_estimate,
    get_business_by_id,
    list_estimates,
    pipeline_stats,
    pricing_tiers,
    process_due_follow_ups,
    recent_messages,
    set_estimate_status,
    trade_catalog,
)
from closeloop.trades import get_trade

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.filters["money"] = lambda v: f"${float(v or 0):,.0f}"
templates.env.filters["datefmt"] = lambda v: v.strftime("%b %d, %Y") if v else "—"

scheduler: BackgroundScheduler | None = None


def _scheduled_followups() -> None:
    with db_module.SessionLocal() as db:
        process_due_follow_ups(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global scheduler
    init_db()
    settings = get_settings()
    if settings.seed_demo:
        with db_module.SessionLocal() as db:
            seed_demo(db)

    scheduler = BackgroundScheduler()
    scheduler.add_job(_scheduled_followups, "interval", minutes=15, id="followups")
    scheduler.start()
    try:
        yield
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)


app = FastAPI(title="CloseLoop", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key, https_only=False)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _current_business(request: Request, db: Session) -> Business | None:
    biz_id = request.session.get("business_id")
    if not biz_id:
        return None
    return get_business_by_id(db, int(biz_id))


def _require_business(request: Request, db: Session) -> Business:
    biz = _current_business(request, db)
    if not biz:
        raise HTTPException(status_code=303, detail="login", headers={"Location": "/login"})
    return biz


def _login_redirect() -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "app_name": settings.app_name,
            "app_base_url": settings.app_base_url,
            "register_url": f"{settings.app_base_url.rstrip('/')}{settings.register_path}",
            "trades": trade_catalog(),
            "tiers": pricing_tiers(),
            "business": _current_business(request, db),
            "steps": STEP_BY_STEP_REGISTER,
            "advantages": ADVANTAGES,
        },
    )


@app.get("/guide", response_class=HTMLResponse)
def guide(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "guide.html",
        {
            "app_name": settings.app_name,
            "app_base_url": settings.app_base_url,
            "register_url": f"{settings.app_base_url.rstrip('/')}{settings.register_path}",
            "steps": STEP_BY_STEP_REGISTER,
            "advantages": ADVANTAGES,
            "business": _current_business(request, db),
            "tiers": pricing_tiers(),
        },
    )


@app.get("/advertise", response_class=HTMLResponse)
def advertise(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "advertise.html",
        {
            "app_name": settings.app_name,
            "app_base_url": settings.app_base_url,
            "register_url": f"{settings.app_base_url.rstrip('/')}{settings.register_path}",
            "social": SOCIAL_POSTERS,
            "catalogue": CATALOGUE_PAGES,
            "flyer": FLYER_BLURB,
            "advantages": ADVANTAGES,
            "business": _current_business(request, db),
        },
    )


@app.get("/register", response_class=HTMLResponse)
@app.get("/start", response_class=HTMLResponse)
def register_form(request: Request, db: Session = Depends(get_db)):
    if _current_business(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    plan = request.query_params.get("plan", "growth")
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "app_name": get_settings().app_name,
            "trades": trade_catalog(),
            "tiers": pricing_tiers(),
            "selected_plan": plan,
            "error": "",
            "steps": STEP_BY_STEP_REGISTER,
            "business": None,
        },
    )


@app.post("/register")
def register_submit(
    request: Request,
    name: str = Form(...),
    owner_name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(...),
    password: str = Form(...),
    trade_key: str = Form("roofing"),
    plan_key: str = Form("growth"),
    db: Session = Depends(get_db),
):
    if _current_business(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    if len(password) < 6:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "app_name": get_settings().app_name,
                "trades": trade_catalog(),
                "tiers": pricing_tiers(),
                "selected_plan": plan_key,
                "error": "Password must be at least 6 characters.",
                "steps": STEP_BY_STEP_REGISTER,
                "business": None,
            },
            status_code=400,
        )
    try:
        biz = create_business(
            db,
            name=name,
            owner_name=owner_name,
            phone=phone,
            email=email,
            login_email=email,
            password=password,
            trade_key=trade_key,
            plan_key=plan_key,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "app_name": get_settings().app_name,
                "trades": trade_catalog(),
                "tiers": pricing_tiers(),
                "selected_plan": plan_key,
                "error": str(exc),
                "steps": STEP_BY_STEP_REGISTER,
                "business": None,
            },
            status_code=400,
        )
    request.session["business_id"] = biz.id
    return RedirectResponse("/estimates/new?welcome=1", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, db: Session = Depends(get_db)):
    if _current_business(request, db):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"app_name": get_settings().app_name, "error": "", "business": None},
    )


@app.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    biz = authenticate_business(db, email, password)
    if not biz:
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "app_name": get_settings().app_name,
                "error": "Invalid email or password.",
                "business": None,
            },
            status_code=400,
        )
    request.session["business_id"] = biz.id
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    stats = pipeline_stats(db, biz.id)
    estimates = list_estimates(db, biz.id)
    messages = recent_messages(db, biz.id, limit=12)
    today = date.today()
    call_scripts = list(
        db.scalars(
            select(FollowUp)
            .options(joinedload(FollowUp.estimate))
            .join(Estimate)
            .where(
                Estimate.business_id == biz.id,
                Estimate.status == "open",
                FollowUp.channel == "call_script",
                FollowUp.status == "pending",
                FollowUp.scheduled_for <= today,
            )
            .order_by(FollowUp.scheduled_for)
        ).unique()
    )
    trade = get_trade(biz.trade_key)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "app_name": get_settings().app_name,
            "business": biz,
            "trade": trade,
            "stats": stats,
            "estimates": estimates,
            "messages": messages,
            "call_scripts": call_scripts,
            "trades": trade_catalog(),
            "today": today,
        },
    )


@app.get("/estimates/new", response_class=HTMLResponse)
def new_estimate_form(request: Request, db: Session = Depends(get_db)):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    return templates.TemplateResponse(
        request,
        "estimate_form.html",
        {
            "app_name": get_settings().app_name,
            "business": biz,
            "trades": trade_catalog(),
            "today": date.today().isoformat(),
            "welcome": request.query_params.get("welcome") == "1",
        },
    )


@app.post("/estimates")
def create_estimate_route(
    request: Request,
    homeowner_name: str = Form(...),
    homeowner_phone: str = Form(""),
    homeowner_email: str = Form(""),
    address: str = Form(""),
    job_title: str = Form(""),
    amount: float = Form(0),
    trade_key: str = Form(""),
    quoted_on: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    qdate = date.fromisoformat(quoted_on) if quoted_on else date.today()
    create_estimate(
        db,
        biz,
        homeowner_name=homeowner_name,
        homeowner_phone=homeowner_phone,
        homeowner_email=homeowner_email,
        address=address,
        job_title=job_title,
        amount=amount,
        trade_key=trade_key or biz.trade_key,
        quoted_on=qdate,
        notes=notes,
        send_due_now=True,
    )
    return RedirectResponse("/dashboard?added=1", status_code=303)


@app.get("/estimates/{estimate_id}", response_class=HTMLResponse)
def estimate_detail(estimate_id: int, request: Request, db: Session = Depends(get_db)):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    estimate = db.scalar(
        select(Estimate)
        .options(joinedload(Estimate.follow_ups))
        .where(Estimate.id == estimate_id, Estimate.business_id == biz.id)
    )
    if not estimate:
        raise HTTPException(404, "Estimate not found")
    trade = get_trade(estimate.trade_key or biz.trade_key)
    return templates.TemplateResponse(
        request,
        "estimate_detail.html",
        {
            "app_name": get_settings().app_name,
            "business": biz,
            "estimate": estimate,
            "trade": trade,
            "today": date.today(),
        },
    )


@app.post("/estimates/{estimate_id}/status")
def update_status(
    estimate_id: int,
    request: Request,
    status: str = Form(...),
    lost_reason: str = Form(""),
    db: Session = Depends(get_db),
):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    estimate = db.scalar(
        select(Estimate)
        .options(joinedload(Estimate.follow_ups))
        .where(Estimate.id == estimate_id, Estimate.business_id == biz.id)
    )
    if not estimate:
        raise HTTPException(404, "Estimate not found")
    set_estimate_status(db, estimate, status, lost_reason=lost_reason)
    return RedirectResponse(f"/estimates/{estimate_id}", status_code=303)


@app.post("/run-followups")
def run_followups_now(request: Request, db: Session = Depends(get_db)):
    biz = _current_business(request, db)
    if not biz:
        return _login_redirect()
    stats = process_due_follow_ups(db)
    return RedirectResponse(f"/dashboard?ran={stats['sent']}", status_code=303)


# Keep old /onboard URL working as an alias to public register.
@app.get("/onboard")
def onboard_alias():
    return RedirectResponse("/register", status_code=303)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "closeloop", "time": datetime.utcnow().isoformat()}


@app.get("/api/stats")
def api_stats(request: Request, db: Session = Depends(get_db)):
    biz = _current_business(request, db)
    if not biz:
        raise HTTPException(401, "Login required")
    return pipeline_stats(db, biz.id)