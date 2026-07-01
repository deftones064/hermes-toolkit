PLANNED_HOME_ASSISTANT_AREAS = [
    {
        "name": "Connection Status",
        "status": "Planned",
        "description": "Future read-only status for Home Assistant URL, token presence, and connectivity health.",
        "icon": "plug-zap",
    },
    {
        "name": "Entity Inventory",
        "status": "Planned",
        "description": "Future read-only summary of exposed entities, domains, devices, and areas.",
        "icon": "house-plug",
    },
    {
        "name": "Automation Hooks",
        "status": "Planned",
        "description": "Future read-only view of Hermes-to-Home-Assistant automation hook readiness.",
        "icon": "workflow",
    },
    {
        "name": "Notifications",
        "status": "Planned",
        "description": "Future readiness view for notify services, alert channels, and event delivery.",
        "icon": "bell",
    },
]


def build_home_assistant_readiness_items(cfg):
    toolkit_cfg = cfg.get("toolkit") or {}
    ha_cfg = toolkit_cfg.get("home_assistant") or {}

    has_url = bool(ha_cfg.get("url"))
    has_token = bool(ha_cfg.get("token") or ha_cfg.get("token_env"))
    has_webhook = bool(ha_cfg.get("webhook_url") or ha_cfg.get("webhook_id"))

    return [
        {
            "name": "Connection Config",
            "status": "available" if has_url else "planned",
            "summary": "Home Assistant URL detected." if has_url else "No Home Assistant URL configured yet.",
            "detail": "Future live checks can use this config without controlling devices or services.",
            "icon": "link",
        },
        {
            "name": "Auth Readiness",
            "status": "available" if has_token else "planned",
            "summary": "Token reference detected." if has_token else "No token or token environment reference configured yet.",
            "detail": "Future auth checks should validate configuration without exposing token values.",
            "icon": "key-round",
        },
        {
            "name": "Webhook Readiness",
            "status": "available" if has_webhook else "planned",
            "summary": "Webhook configuration detected." if has_webhook else "No webhook configuration detected yet.",
            "detail": "Future webhook support can remain explicit and opt-in.",
            "icon": "radio",
        },
        {
            "name": "Action Safety",
            "status": "available",
            "summary": "Home Assistant foundation is read-only.",
            "detail": "No entities, devices, services, automations, or scripts are called by this foundation.",
            "icon": "shield-check",
        },
    ]


def build_home_assistant_data(dashboard_data, cfg):
    data = dict(dashboard_data)
    readiness_items = build_home_assistant_readiness_items(cfg)

    data["home_assistant_page"] = {
        "status": "Foundation",
        "status_class": "warn",
        "detail": "Home Assistant foundation is read-only and does not call entities, devices, services, automations, or scripts.",
        "planned_areas": PLANNED_HOME_ASSISTANT_AREAS,
        "readiness_items": readiness_items,
        "readiness_count": len(readiness_items),
        "available_readiness_count": sum(
            1 for item in readiness_items
            if item["status"] == "available"
        ),
        "note": "Home Assistant v1 foundation is read-only. It provides planning and readiness structure without connecting to Home Assistant or controlling anything.",
    }

    return data
