PLANNED_TELEGRAM_AREAS = [
    {
        "name": "Bot Config",
        "status": "Planned",
        "description": "Future read-only status for Telegram bot token presence and bot configuration readiness.",
        "icon": "bot",
    },
    {
        "name": "Chat Targets",
        "status": "Planned",
        "description": "Future read-only inventory of configured chat IDs, channels, or notification destinations.",
        "icon": "messages-square",
    },
    {
        "name": "Notification Routing",
        "status": "Planned",
        "description": "Future readiness view for routing Hermes alerts, summaries, and status updates to Telegram.",
        "icon": "route",
    },
    {
        "name": "Command Hooks",
        "status": "Planned",
        "description": "Future explicit command hook readiness for approved Telegram-to-Hermes workflows.",
        "icon": "terminal-square",
    },
]


def build_telegram_readiness_items(cfg):
    toolkit_cfg = cfg.get("toolkit") or {}
    telegram_cfg = toolkit_cfg.get("telegram") or {}

    has_bot_token = bool(
        telegram_cfg.get("bot_token")
        or telegram_cfg.get("bot_token_env")
        or telegram_cfg.get("token_env")
    )
    has_chat_targets = bool(
        telegram_cfg.get("chat_id")
        or telegram_cfg.get("chat_ids")
        or telegram_cfg.get("default_chat_id")
    )
    has_notifications = bool(
        telegram_cfg.get("notifications")
        or telegram_cfg.get("notification_routes")
        or telegram_cfg.get("routes")
    )

    return [
        {
            "name": "Bot Token Config",
            "status": "available" if has_bot_token else "planned",
            "summary": "Bot token reference detected." if has_bot_token else "No bot token reference configured yet.",
            "detail": "Future checks should validate token configuration without exposing token values.",
            "icon": "key-round",
        },
        {
            "name": "Chat Targets",
            "status": "available" if has_chat_targets else "planned",
            "summary": "Chat target configuration detected." if has_chat_targets else "No chat targets configured yet.",
            "detail": "Future chat inventory can remain read-only and avoid contacting chats.",
            "icon": "messages-square",
        },
        {
            "name": "Notification Routes",
            "status": "available" if has_notifications else "planned",
            "summary": "Notification routing config detected." if has_notifications else "No notification routes configured yet.",
            "detail": "Future routing checks can describe planned delivery paths without sending messages.",
            "icon": "route",
        },
        {
            "name": "Action Safety",
            "status": "available",
            "summary": "Telegram foundation is read-only.",
            "detail": "No messages are sent, no chats are contacted, and no bot commands are executed by this foundation.",
            "icon": "shield-check",
        },
    ]


def build_telegram_data(dashboard_data, cfg):
    data = dict(dashboard_data)
    readiness_items = build_telegram_readiness_items(cfg)

    data["telegram_page"] = {
        "status": "Foundation",
        "status_class": "warn",
        "detail": "Telegram foundation is read-only and does not send messages, contact chats, or execute bot commands.",
        "planned_areas": PLANNED_TELEGRAM_AREAS,
        "readiness_items": readiness_items,
        "readiness_count": len(readiness_items),
        "available_readiness_count": sum(
            1 for item in readiness_items
            if item["status"] == "available"
        ),
        "note": "Telegram v1 foundation is read-only. It provides planning and readiness structure without connecting to Telegram or sending messages.",
    }

    return data
