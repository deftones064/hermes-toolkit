from .config import get_path
from .logs import parse_recent_api_calls

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    RICH = True
except Exception:
    RICH = False


def show(cfg):
    if not RICH:
        print("Model:", cfg.get("model"))
        print("Max turns:", get_path(cfg, ("agent", "max_turns")))
        print("max_live_sessions:", cfg.get("max_live_sessions"))
        print("context_file_max_chars:", cfg.get("context_file_max_chars"))
        print("file_read_max_chars:", cfg.get("file_read_max_chars"))
        print("compression.protect_last_n:", get_path(cfg, ("compression", "protect_last_n")))
        print("display.resume_exchanges:", get_path(cfg, ("display", "resume_exchanges")))
        print("session_reset:", cfg.get("session_reset"))
        return

    console = Console()
    model = cfg.get("model", {})
    table = Table(title="Hermes Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Provider", str(model.get("provider")))
    table.add_row("Model", str(model.get("default")))
    table.add_row("Base URL", str(model.get("base_url")))
    table.add_row("Max turns", str(get_path(cfg, ("agent", "max_turns"))))
    table.add_row("Max live sessions", str(cfg.get("max_live_sessions")))
    table.add_row("Context file max chars", str(cfg.get("context_file_max_chars")))
    table.add_row("File read max chars", str(cfg.get("file_read_max_chars")))
    table.add_row("Protected recent messages", str(get_path(cfg, ("compression", "protect_last_n"))))
    table.add_row("Resume exchanges", str(get_path(cfg, ("display", "resume_exchanges"))))
    table.add_row("Session reset", str(cfg.get("session_reset")))

    console.print(table)


def status(cfg):
    calls = parse_recent_api_calls()

    if not RICH:
        show(cfg)
        print()
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
        return

    console = Console()
    model = cfg.get("model", {})

    if calls:
        avg_in = sum(c["in"] for c in calls) / len(calls)
        avg_out = sum(c["out"] for c in calls) / len(calls)
        avg_cache = sum(c["pct"] for c in calls) / len(calls)
        latest = calls[-1]

        if avg_in > 100000:
            prompt_status = "[red]High[/red]"
        elif avg_in > 60000:
            prompt_status = "[yellow]Moderate[/yellow]"
        else:
            prompt_status = "[green]Controlled[/green]"

        if avg_cache < 50:
            cache_status = "[red]Low[/red]"
        elif avg_cache < 85:
            cache_status = "[yellow]Okay[/yellow]"
        else:
            cache_status = "[green]Good[/green]"

        summary = (
            f"[bold]Provider:[/bold] {model.get('provider')}\n"
            f"[bold]Model:[/bold] {model.get('default')}\n"
            f"[bold]Prompt usage:[/bold] {prompt_status}\n"
            f"[bold]Cache:[/bold] {cache_status}"
        )
        console.print(Panel(summary, title="Hermes Toolkit Status", box=box.ROUNDED))

        usage = Table(title="Recent API Usage", box=box.ROUNDED)
        usage.add_column("Metric", style="cyan")
        usage.add_column("Value", style="green")
        usage.add_row("Calls analyzed", str(len(calls)))
        usage.add_row("Latest model", f"{latest['provider']} / {latest['model']}")
        usage.add_row("Latest input tokens", f"{latest['in']:,}")
        usage.add_row("Latest output tokens", f"{latest['out']:,}")
        usage.add_row("Latest total tokens", f"{latest['total']:,}")
        usage.add_row("Latest cache hit", f"{latest['pct']}%")
        usage.add_row("Average input tokens", f"{avg_in:,.0f}")
        usage.add_row("Average output tokens", f"{avg_out:,.0f}")
        usage.add_row("Average cache hit", f"{avg_cache:.1f}%")
        console.print(usage)
    else:
        console.print(Panel("No recent API call stats found.", title="Hermes Toolkit Status"))

    config = Table(title="Active Configuration", box=box.ROUNDED)
    config.add_column("Setting", style="cyan")
    config.add_column("Value", style="green")
    config.add_row("Max turns", str(get_path(cfg, ("agent", "max_turns"))))
    config.add_row("Max live sessions", str(cfg.get("max_live_sessions")))
    config.add_row("Context file max chars", str(cfg.get("context_file_max_chars")))
    config.add_row("File read max chars", str(cfg.get("file_read_max_chars")))
    config.add_row("Protected recent messages", str(get_path(cfg, ("compression", "protect_last_n"))))
    config.add_row("Resume exchanges", str(get_path(cfg, ("display", "resume_exchanges"))))
    config.add_row("Session reset", str(cfg.get("session_reset")))
    console.print(config)
