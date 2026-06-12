from pydantic import Field

from app.db.repository import GrantPilotRepository
from app.models import APIModel
from app.services.agent_activity_service import build_agent_activity
from app.services.dashboard_service import build_dashboard


def _enum_value(value: object) -> object:
    return value.value if hasattr(value, "value") else value


class OpenUIComponent(APIModel):
    type: str
    id: str
    props: dict[str, object] = Field(default_factory=dict)
    children: list["OpenUIComponent"] = Field(default_factory=list)


class OpenUILayout(APIModel):
    title: str
    description: str
    components: list[OpenUIComponent] = Field(default_factory=list)


def build_openui_layout(storage: GrantPilotRepository) -> OpenUILayout:
    dashboard = build_dashboard(storage)
    activity = build_agent_activity(storage)

    ranked_cards = [
        OpenUIComponent(
            type="opportunity_card",
            id=f"opp_card_{item.match.id}",
            props={
                "title": item.opportunity.title,
                "provider": item.opportunity.provider_name,
                "score_percent": item.score_percent,
                "success_probability": item.success_probability,
                "priority": item.priority,
                "deadline": item.opportunity.deadline.isoformat() if item.opportunity.deadline else None,
                "tags": item.opportunity.tags,
            },
        )
        for item in dashboard.ranked_opportunities[:5]
    ]

    match_panels = [
        OpenUIComponent(
            type="match_panel",
            id=f"match_panel_{match.id}",
            props={
                "opportunity_id": match.opportunity_id,
                "score": match.score,
                "priority": _enum_value(match.priority),
                "fit_explanation": match.fit_explanation or match.rationale,
                "recommended_actions": match.recommended_actions,
                "missing_materials": match.missing_materials,
            },
        )
        for match in dashboard.top_matches
    ]

    pipeline_rows = [
        OpenUIComponent(
            type="pipeline_row",
            id=f"pipeline_{app.id}",
            props={
                "application_id": app.id,
                "status": _enum_value(app.status),
                "due_at": app.due_at.isoformat() if app.due_at else None,
                "checklist_total": len(app.checklist),
                "checklist_done": sum(1 for item in app.checklist if _enum_value(item.status) == "done"),
            },
        )
        for app in dashboard.applications
    ]

    notification_items = [
        OpenUIComponent(
            type="notification_item",
            id=f"notif_{item.id}",
            props={
                "title": item.title,
                "message": item.message,
                "type": _enum_value(item.notification_type),
                "priority": _enum_value(item.priority),
                "is_read": item.is_read,
                "action_url": item.action_url,
            },
        )
        for item in dashboard.notifications
    ]

    timeline_items = [
        OpenUIComponent(
            type="timeline_event",
            id=f"timeline_{log.id}",
            props={
                "agent_name": log.agent_name,
                "action_type": log.action_type,
                "status": _enum_value(log.status),
                "input_summary": log.input_summary,
                "output_summary": log.output_summary,
                "runtime_ms": log.metadata.get("runtime_ms"),
                "guild_run_id": log.metadata.get("guild_run_id"),
                "created_at": log.created_at.isoformat(),
            },
        )
        for log in activity.recent_actions
    ]

    return OpenUILayout(
        title="GrantPilot Agent Workspace",
        description="Dynamic OpenUI layout generated from live agent activity and workspace state.",
        components=[
            OpenUIComponent(
                type="section",
                id="section_opportunities",
                props={"title": "Opportunity Cards", "layout": "grid"},
                children=ranked_cards,
            ),
            OpenUIComponent(
                type="section",
                id="section_matches",
                props={"title": "Match Panels", "layout": "stack"},
                children=match_panels,
            ),
            OpenUIComponent(
                type="section",
                id="section_pipeline",
                props={"title": "Application Pipeline", "layout": "table"},
                children=pipeline_rows,
            ),
            OpenUIComponent(
                type="section",
                id="section_notifications",
                props={"title": "Notification Feed", "layout": "feed"},
                children=notification_items,
            ),
            OpenUIComponent(
                type="section",
                id="section_timeline",
                props={"title": "Agent Timeline", "layout": "timeline"},
                children=timeline_items,
            ),
        ],
    )
