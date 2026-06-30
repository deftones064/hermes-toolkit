from .config import get_path
from .status import status

def doctor(cfg):
    issues = []

    if get_path(cfg, ("agent", "max_turns"), 999) > 50:
        issues.append("agent.max_turns is high")
    if cfg.get("context_file_max_chars") is None:
        issues.append("context_file_max_chars is unlimited")
    if cfg.get("file_read_max_chars", 999999) > 60000:
        issues.append("file_read_max_chars is high")
    if get_path(cfg, ("compression", "protect_last_n"), 999) > 15:
        issues.append("compression.protect_last_n is high")
    if get_path(cfg, ("session_reset", "mode")) == "none":
        issues.append("session_reset is disabled")
    if "idle" in cfg.get("session_reset", {}):
        issues.append("stray session_reset.idle key exists")

    if not issues:
        print("Hermes settings look good.")
    else:
        print("Potential issues:")
        for i in issues:
            print(f"  - {i}")

    print()
    status(cfg)
