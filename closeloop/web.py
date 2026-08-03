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

import closeloop.db as db_module
from closeloop.config import get_settings
from closeloop.db import get_db, init_db
from closeloop.models import Estimate, FollowUp
from closeloop.seed import seed_demo
from closeloop.service import (
    create_business,
    create_estimate,
    get_default_business,
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
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _biz_or_404(db: Session):
    biz = get_default_business(db)
    if not biz:
        raise HTTPException(404, "No business configured. POST /onboard first.")
    return biz


@app.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "app_name": get_settings().app_name,
            "trades": trade_catalog(),
            "tiers": pricing_tiers(),
            "has_business": get_default_business(db) is not None,
        },
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    biz = _biz_or_404(db)
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
    biz = _biz_or_404(db)
    return templates.TemplateResponse(
        request,
        "estimate_form.html",
        {
            "app_name": get_settings().app_name,
            "business": biz,
            "trades": trade_catalog(),
            "today": date.today().isoformat(),
        },
    )


@app.post("/estimates")
def create_estimate_route(
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
    biz = _biz_or_404(db)
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
    )
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/estimates/{estimate_id}", response_class=HTMLResponse)
def estimate_detail(estimate_id: int, request: Request, db: Session = Depends(get_db)):
    biz = _biz_or_404(db)
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
    status: str = Form(...),
    lost_reason: str = Form(""),
    db: Session = Depends(get_db),
):
    biz = _biz_or_404(db)
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
def run_followups_now(db: Session = Depends(get_db)):
    _biz_or_404(db)
    stats = process_due_follow_ups(db)
    return RedirectResponse(f"/dashboard?ran={stats['sent']}", status_code=303)


@app.get("/onboard", response_class=HTMLResponse)
def onboard_form(request: Request, db: Session = Depends(get_db)):
    if get_default_business(db):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "onboard.html",
        {
            "app_name": get_settings().app_name,
            "trades": trade_catalog(),
            "tiers": pricing_tiers(),
        },
    )


@app.post("/onboard")
def onboard_submit(
    name: str = Form(...),
    owner_name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    trade_key: str = Form("roofing"),
    plan_key: str = Form("growth"),
    db: Session = Depends(get_db),
):
    if get_default_business(db):
        return RedirectResponse("/dashboard", status_code=303)
    create_business(
        db,
        name=name,
        owner_name=owner_name,
        phone=phone,
        email=email,
        trade_key=trade_key,
        plan_key=plan_key,
    )
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "closeloop", "time": datetime.utcnow().isoformat()}


@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    biz = _biz_or_404(db)
    return pipeline_stats(db, biz.id)