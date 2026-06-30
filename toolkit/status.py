from .config import get_path
from .logs import parse_recent_api_calls

def show(cfg):
    print("Model:", cfg.get("model"))
    print("Max turns:", get_path(cfg, ("agent", "max_turns")))
    print("max_live_sessions:", cfg.get("max_live_sessions"))
    print("context_file_max_chars:", cfg.get("context_file_max_chars"))
    print("file_read_max_chars:", cfg.get("file_read_max_chars"))
    print("compression.protect_last_n:", get_path(cfg, ("compression", "protect_last_n")))
    print("display.resume_exchanges:", get_path(cfg, ("display", "resume_exchanges")))
    print("session_reset:", cfg.get("session_reset"))

def status(cfg):
    show(cfg)
    print()

    calls = parse_recent_api_calls()
    if not calls:
        print("No recent API call stats found.")
        return

    avg_in = sum(c["in"] for c in calls) / len(calls)
    avg_out = sum(c["out"] for c in calls) / len(calls)
    avg_cache = sum(c["pct"] for c in calls) / len(calls)
    latest = calls[-1]

    print("Recent API usage:")
    print(f"  Calls analyzed: {len(calls)}")
    print(f"  Latest model: {latest['provider']} / {latest['model']}")
    print(f"  Latest tokens: in={latest['in']} out={latest['out']} total={latest['total']}")
    print(f"  Latest cache: {latest['pct']}%")
    print(f"  Avg input tokens: {avg_in:,.0f}")
    print(f"  Avg output tokens: {avg_out:,.0f}")
    print(f"  Avg cache hit: {avg_cache:.1f}%")
    print()

    if avg_in > 100000:
        print("Status: High prompt usage")
    elif avg_in > 60000:
        print("Status: Moderate prompt usage")
    else:
        print("Status: Prompt usage looks controlled")

    if avg_cache < 50:
        print("Cache: Low cache hit rate")
    elif avg_cache < 85:
        print("Cache: Cache could be better")
    else:
        print("Cache: Cache hit rate looks good")
