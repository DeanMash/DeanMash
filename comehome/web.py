"""FastAPI app: marketing site + operator dashboard API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config
from .engine import WinBackEngine
from .messaging import MessageSender
from .pricing import list_plans
from .store import Store, client_to_dict
from .verticals import list_verticals

STATIC = Path(__file__).resolve().parent / "static"


class AddClientBody(BaseModel):
    full_name: str
    phone: str
    last_visit: str
    staff_name: str = ""
    notes: str = ""


class RecoverBody(BaseModel):
    client_id: str


class LeadBody(BaseModel):
    name: str
    business: str
    vertical: str = "gym"
    phone: str
    city: str = "Harare"
    plan: str = "practice"
    message: str = ""


def create_app(store: Store | None = None) -> FastAPI:
    store = store or Store()
    engine = WinBackEngine(store, MessageSender())
    app = FastAPI(title="ComeHome", version="0.1.0")

    # Ensure demo data exists for first boot.
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
        return {"status": "ok", "product": "ComeHome"}

    @app.get("/api/verticals")
    def verticals() -> list[dict[str, Any]]:
        return [
            {
                "key": v.key,
                "label": v.label,
                "why": v.why,
                "lapse_signal": v.lapse_signal,
                "channel_note": v.channel_note,
            }
            for v in list_verticals()
        ]

    @app.get("/api/plans")
    def plans() -> list[dict[str, Any]]:
        return list_plans()

    @app.get("/api/business")
    def business(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        biz = store.get_business(_biz_id(business_id))
        if not biz:
            raise HTTPException(status_code=404, detail="Business not found")
        return {
            "id": biz.id,
            "name": biz.name,
            "vertical": biz.vertical,
            "city": biz.city,
            "staff_name": biz.staff_name,
            "booking_link": biz.booking_link,
            "offer": biz.offer,
            "plan": biz.plan,
            "whatsapp_from": biz.whatsapp_from,
        }

    @app.get("/api/stats")
    def stats(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        return store.stats(_biz_id(business_id))

    @app.get("/api/clients")
    def clients(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_comehome_token)
        return [client_to_dict(c) for c in store.list_clients(_biz_id(business_id))]

    @app.post("/api/clients")
    def add_client(
        body: AddClientBody,
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        bid = _biz_id(business_id)
        client = store.add_client(bid, **body.model_dump())
        engine.plan_client(bid, client)
        return client_to_dict(client)

    @app.get("/api/messages")
    def messages(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_comehome_token)
        return [m.__dict__ for m in store.list_messages(_biz_id(business_id))]

    @app.get("/api/events")
    def events(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> list[dict[str, Any]]:
        _auth(x_comehome_token)
        return store.recent_events(_biz_id(business_id))

    @app.post("/api/plan")
    def plan(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        return engine.plan_business(_biz_id(business_id))

    @app.post("/api/run")
    def run(
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        return engine.run_due(_biz_id(business_id))

    @app.post("/api/recover")
    def recover(
        body: RecoverBody,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        client = engine.mark_recovered(body.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client_to_dict(client)

    @app.get("/api/preview")
    def preview(
        client_id: str = Query(...),
        day: int = Query(30),
        business_id: str | None = None,
        x_comehome_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _auth(x_comehome_token)
        result = engine.preview(_biz_id(business_id), client_id, day)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result

    @app.post("/api/leads")
    def leads(body: LeadBody) -> dict[str, str]:
        # Store enquiry as an event on the demo business for the operator inbox.
        bid = _biz_id(None)
        store.add_event(
            bid,
            "lead",
            body.model_dump(),
        )
        return {"status": "received", "next": "We will WhatsApp you within one business day."}

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/dashboard")
    def dashboard() -> FileResponse:
        return FileResponse(STATIC / "dashboard.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()
