"""FastAPI app: marketing site + operator dashboard API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .engine import OutreachEngine
from .messaging import MessageSender
from .pricing import list_plans
from .store import Store, prospect_to_dict
from .verticals import list_verticals

STATIC = Path(__file__).resolve().parent / "static"


class AddProspectBody(BaseModel):
    full_name: str
    email: str
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


def create_app(store: Store | None = None) -> FastAPI:
    store = store or Store()
    engine = OutreachEngine(store, MessageSender())
    app = FastAPI(title="OpenPipe", version="0.1.0")

    biz = store.seed_demo()
    engine.plan_business(biz.id)

    def _auth(token: str | None) -> None:
        expected = config.DASHBOARD_TOKEN
        if expected and token != expected:
            raise HTTPException(status_code=401, detail="Invalid dashboard token")

    def _biz_id(business_id: str | None) -> str:
        if business_id:
            return business_id
        businesses = store.list_businesses()
        if not businesses:
            raise HTTPException(status_code=404, detail="No business")
        return businesses[0].id

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "product": "OpenPipe"}

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

    @app.get("/api/business")
    def business(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        biz = store.get_business(_biz_id(business_id))
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")
        return {
            "id": biz.id,
            "name": biz.name,
            "vertical": biz.vertical,
            "city": biz.city,
            "sender_name": biz.sender_name,
            "sender_email": biz.sender_email,
            "booking_link": biz.booking_link,
            "offer": biz.offer,
            "plan": biz.plan,
            "niche": biz.niche,
        }

    @app.get("/api/stats")
    def stats(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        return store.stats(_biz_id(business_id))

    @app.get("/api/prospects")
    def prospects(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_openpipe_token)
        return [prospect_to_dict(p) for p in store.list_prospects(_biz_id(business_id))]

    @app.post("/api/prospects")
    def add_prospect(
        body: AddProspectBody,
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        bid = _biz_id(business_id)
        prospect = store.add_prospect(bid, **body.model_dump())
        engine.plan_prospect(bid, prospect)
        return prospect_to_dict(prospect)

    @app.post("/api/discover")
    def discover(
        body: DiscoverBody,
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        return engine.discover_and_plan(
            _biz_id(business_id),
            limit=body.limit,
            city=body.city,
            niche=body.niche,
        )

    @app.get("/api/messages")
    def messages(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_openpipe_token)
        return [m.__dict__ for m in store.list_messages(_biz_id(business_id))]

    @app.get("/api/events")
    def events(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        _auth(x_openpipe_token)
        return store.recent_events(_biz_id(business_id))

    @app.post("/api/plan")
    def plan(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        return engine.plan_business(_biz_id(business_id))

    @app.post("/api/run")
    def run(
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        return engine.run_due(_biz_id(business_id))

    @app.post("/api/replied")
    def replied(
        body: ProspectActionBody,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        prospect = engine.mark_replied(body.prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        return prospect_to_dict(prospect)

    @app.post("/api/meeting")
    def meeting(
        body: ProspectActionBody,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        prospect = engine.mark_meeting(body.prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        return prospect_to_dict(prospect)

    @app.get("/api/preview")
    def preview(
        prospect_id: str = Query(...),
        day: int = Query(0),
        business_id: str | None = None,
        x_openpipe_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_openpipe_token)
        result = engine.preview(_biz_id(business_id), prospect_id, day)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result

    @app.post("/api/leads")
    def leads(body: LeadBody) -> dict[str, str]:
        bid = _biz_id(None)
        store.add_event(bid, "lead", body.model_dump())
        return {
            "status": "received",
            "next": "We'll email you within one business day with a walkthrough.",
        }

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/dashboard")
    def dashboard() -> FileResponse:
        return FileResponse(STATIC / "dashboard.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()
