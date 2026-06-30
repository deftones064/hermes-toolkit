PROFILES = {
    "low-cost": {
        ("agent", "max_turns"): 30,
        ("context_file_max_chars",): 40000,
        ("file_read_max_chars",): 30000,
        ("compression", "protect_last_n"): 10,
        ("display", "resume_exchanges"): 5,
        ("session_reset", "mode"): "idle",
        ("session_reset", "idle_minutes"): 120,
        ("max_live_sessions",): 8,
    },
    "balanced": {
        ("agent", "max_turns"): 50,
        ("context_file_max_chars",): 80000,
        ("file_read_max_chars",): 60000,
        ("compression", "protect_last_n"): 15,
        ("display", "resume_exchanges"): 8,
        ("session_reset", "mode"): "idle",
        ("session_reset", "idle_minutes"): 240,
        ("max_live_sessions",): 12,
    },
    "premium": {
        ("agent", "max_turns"): 100,
        ("context_file_max_chars",): None,
        ("file_read_max_chars",): 100000,
        ("compression", "protect_last_n"): 20,
        ("display", "resume_exchanges"): 10,
        ("session_reset", "mode"): "none",
        ("max_live_sessions",): 16,
    },
}

def apply_profile(cfg, name, set_path):
    if name not in PROFILES:
        raise SystemExit("Unknown profile. Use: low-cost, balanced, premium")
    for path, value in PROFILES[name].items():
        set_path(cfg, path, value)
