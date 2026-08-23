"""FastAPI app: marketing site, org registration, operator dashboard API."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .channels import CHANNEL_CHOICES, normalize_channels
from .engine import OutreachEngine
from .messaging import MessageSender
from .pricing import list_plans
from .starters import list_starters
from .store import Store, business_to_dict, prospect_to_dict
from .templates_msg import DEFAULT_OFFERS, sample_sequences
from .verticals import list_verticals

STATIC = Path(__file__).resolve().parent / "static"
log = logging.getLogger("openpipe.web")


class AddProspectBody(BaseModel):
    full_name: str
    email: str = ""
    phone: str = ""
    title: str = ""
    company: str = ""
    industry: str = ""
    city: str = ""
    company_size: str = ""
    trigger: str = ""
    notes: str = ""


class ProspectActionBody(BaseModel):
    prospect_id: str


class DiscoverBody(BaseModel):
    limit: int = Field(default=8, ge=1, le=50)
    city: str | None = None
    niche: str | None = None


class LeadBody(BaseModel):
    name: str
    business: str
    vertical: str = "insurance"
    email: str
    phone: str = ""
    city: str = "Harare"
    plan: str = "pipeline"
    message: str = ""


class RegisterBody(BaseModel):
    owner_name: str
    business_name: str
    vertical: str = "insurance"
    email: str
    phone: str = ""
    city: str = "Harare"
    niche: str = ""
    plan: str = "starter"
    channels: str = "both"
    offer: str = ""
    seed_prospects: bool = True


class LoginBody(BaseModel):
    email: str = ""
    access_token: str = ""


class SettingsBody(BaseModel):
    channels: str | None = None
    niche: str | None = None
    offer: str | None = None
    city: str | None = None
    whatsapp_from: str | None = None
    auto_run: int | None = None
    booking_link: str | None = None


def create_app(store: Store | None = None) -> FastAPI:
    store = store or Store()
    engine = OutreachEngine(store, MessageSender())
    app = FastAPI(title="OpenPipe", version="0.2.0")

    store.seed_demo()
    for biz in store.list_businesses():
        if biz.id.startswith("demo-"):
            engine.plan_business(biz.id)

    def _start_auto_runner() -> None:
        if not config.AUTO_RUN_ENABLED:
            return

        def loop() -> None:
            while True:
                try:
                    result = engine.run_auto()
                    if result["sent"] or result["failed"]:
                        log.info("auto_run %s", result)
                except Exception:  # noqa: BLE001
                    log.exception("auto_run failed")
                time.sleep(config.AUTO_RUN_INTERVAL_SEC)

        thread = threading.Thread(target=loop, name="openpipe-auto-run", daemon=True)
        thread.start()

    _start_auto_runner()

    def _auth(
        token: str | None,
        *,
        business_id: str | None = None,
        allow_open_demo: bool = True,
    ) -> None:
        expected = config.DASHBOARD_TOKEN
        if expected and token == expected:
            return
        if token:
            by_token = store.get_business_by_token(token)
            if by_token:
                if business_id and by_token.id != business_id:
                    raise HTTPException(status_code=403, detail="Token does not match business")
                return
        if business_id:
            biz = store.get_business(business_id)
            if biz and biz.access_token and token == biz.access_token:
                return
            if biz and not biz.access_token and allow_open_demo and not expected:
                return
        if allow_open_demo and not expected:
            return
        if expected:
            raise HTTPException(status_code=401, detail="Invalid dashboard token")
        raise HTTPException(status_code=401, detail="Access token required")

    def _resolve_business_id(
        business_id: str | None,
        token: str | None,
    ) -> str:
        if token:
            by_token = store.get_business_by_token(token)
            if by_token:
                if business_id and business_id != by_token.id:
                    raise HTTPException(status_code=403, detail="Token does not match business")
                return by_token.id
        if business_id:
            return business_id
        businesses = store.list_businesses()
        if not businesses:
            raise HTTPException(status_code=404, detail="No business")
        for b in businesses:
            if b.id == "demo-insurance" or b.vertical == "insurance":
                return b.id
        return businesses[0].id

    def _biz_payload(biz, *, include_token: bool = False) -> dict[str, Any]:
        payload = business_to_dict(biz, include_token=include_token)
        for s in list_starters():
            if s["id"] == biz.id or s["vertical"] == biz.vertical:
                payload["blurb"] = s.get("blurb", "")
                payload["start_tip"] = s.get("start_tip", "")
                break
        else:
            payload["blurb"] = ""
            payload["start_tip"] = (
                "Register, find prospects, preview email/WhatsApp copy, then send."
            )
        return payload

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "product": "OpenPipe",
            "channels": list(CHANNEL_CHOICES),
            "version": "0.2.0",
        }

    @app.get("/api/verticals")
    def verticals() -> list[dict[str, Any]]:
        return [
            {
                "key": v.key,
                "label": v.label,
                "why": v.why,
                "icp": v.icp,
                "trigger_note": v.trigger_note,
            }
            for v in list_verticals()
        ]

    @app.get("/api/plans")
    def plans() -> list[dict[str, Any]]:
        return list_plans()

    @app.get("/api/starters")
    def starters() -> list[dict[str, Any]]:
        return list_starters()

    @app.get("/api/samples")
    def samples() -> list[dict[str, Any]]:
        return sample_sequences()

    @app.post("/api/register")
    def register(body: RegisterBody) -> dict[str, Any]:
        channels = normalize_channels(body.channels)
        try:
            biz = store.register_business(
                owner_name=body.owner_name,
                business_name=body.business_name,
                vertical=body.vertical,
                owner_email=body.email,
                owner_phone=body.phone,
                city=body.city,
                niche=body.niche,
                plan=body.plan,
                channels=channels,
                offer=body.offer or DEFAULT_OFFERS.get(body.vertical, ""),
                sender_name=body.owner_name,
                sender_email=body.email,
                whatsapp_from=body.phone,
                auto_run=1,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        seeded = {"added": 0, "messages_planned": 0}
        if body.seed_prospects:
            seeded = engine.discover_and_plan(biz.id, limit=6)

        return {
            "status": "registered",
            "business": _biz_payload(biz, include_token=True),
            "access_token": biz.access_token,
            "dashboard_url": f"/dashboard?business_id={biz.id}",
            "seeded": seeded,
            "next": "Save your access token — open the dashboard and paste it to manage your pipeline.",
        }

    @app.post("/api/login")
    def login(body: LoginBody) -> dict[str, Any]:
        biz = None
        if body.access_token:
            biz = store.get_business_by_token(body.access_token.strip())
        if not biz and body.email:
            biz = store.get_business_by_owner_email(body.email.strip())
            if biz and body.access_token and biz.access_token != body.access_token.strip():
                raise HTTPException(status_code=401, detail="Invalid access token for that email")
            if biz and not body.access_token:
                raise HTTPException(
                    status_code=401,
                    detail="Enter your access token (shown when you registered).",
                )
        if not biz:
            raise HTTPException(status_code=404, detail="Organisation not found")
        return {
            "status": "ok",
            "business": _biz_payload(biz, include_token=True),
            "access_token": biz.access_token,
            "dashboard_url": f"/dashboard?business_id={biz.id}",
        }

    @app.get("/api/businesses")
    def businesses(
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_openpipe_token)
        if x_openpipe_token:
            by_token = store.get_business_by_token(x_openpipe_token)
            if by_token:
                return [_biz_payload(by_token)]
        return [_biz_payload(b) for b in store.list_businesses()]

    @app.get("/api/business")
    def business(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        biz = store.get_business(bid)
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")
        include = bool(
            x_openpipe_token
            and (
                x_openpipe_token == biz.access_token
                or x_openpipe_token == config.DASHBOARD_TOKEN
            )
        )
        return _biz_payload(biz, include_token=include)

    @app.patch("/api/business")
    def update_business(
        body: SettingsBody,
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        fields = {k: v for k, v in body.model_dump().items() if v is not None}
        if not fields:
            biz = store.get_business(bid)
        else:
            biz = store.update_business(bid, **fields)
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")
        if "channels" in fields:
            engine.plan_business(bid)
        return _biz_payload(biz)

    @app.get("/api/stats")
    def stats(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return store.stats(bid)

    @app.get("/api/prospects")
    def prospects(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return [prospect_to_dict(p) for p in store.list_prospects(bid)]

    @app.post("/api/prospects")
    def add_prospect(
        body: AddProspectBody,
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        if not body.email and not body.phone:
            raise HTTPException(status_code=400, detail="Email or WhatsApp phone required")
        prospect = store.add_prospect(bid, **body.model_dump())
        engine.plan_prospect(bid, prospect)
        return prospect_to_dict(prospect)

    @app.post("/api/discover")
    def discover(
        body: DiscoverBody,
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return engine.discover_and_plan(
            bid,
            limit=body.limit,
            city=body.city,
            niche=body.niche,
        )

    @app.get("/api/messages")
    def messages(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return [m.__dict__ for m in store.list_messages(bid)]

    @app.get("/api/events")
    def events(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return store.recent_events(bid)

    @app.post("/api/plan")
    def plan(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return engine.plan_business(bid)

    @app.post("/api/run")
    def run(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        return engine.run_due(bid)

    @app.post("/api/replied")
    def replied(
        body: ProspectActionBody,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        prospect = store.get_prospect(body.prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        _auth(x_openpipe_token, business_id=prospect.business_id)
        updated = engine.mark_replied(body.prospect_id)
        return prospect_to_dict(updated) if updated else prospect_to_dict(prospect)

    @app.post("/api/meeting")
    def meeting(
        body: ProspectActionBody,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        prospect = store.get_prospect(body.prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        _auth(x_openpipe_token, business_id=prospect.business_id)
        updated = engine.mark_meeting(body.prospect_id)
        return prospect_to_dict(updated) if updated else prospect_to_dict(prospect)

    @app.get("/api/preview")
    def preview(
        prospect_id: str = Query(...),
        day: int = Query(0),
        channel: str = Query("email"),
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        bid = _resolve_business_id(business_id, x_openpipe_token)
        _auth(x_openpipe_token, business_id=bid)
        result = engine.preview(bid, prospect_id, day, channel=channel)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result

    @app.post("/api/leads")
    def leads(body: LeadBody) -> dict[str, str]:
        bid = _resolve_business_id(None, None)
        store.add_event(bid, "lead", body.model_dump())
        return {
            "status": "received",
            "next": "Or register at /register to start sending today.",
        }

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/register")
    def register_page() -> FileResponse:
        return FileResponse(STATIC / "register.html")

    @app.get("/dashboard")
    def dashboard() -> FileResponse:
        return FileResponse(STATIC / "dashboard.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()
