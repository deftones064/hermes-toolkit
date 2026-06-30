#!/usr/bin/env python3
import argparse

from toolkit import __version__
from toolkit.config import load_config, save_config, set_path, parse_value
from toolkit.status import show, status
from toolkit.logs import print_logs
from toolkit.doctor import doctor
from toolkit.profiles import apply_profile
from toolkit.models import apply_model


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hermes-toolkit",
        description="Manage Hermes Agent settings, profiles, models, and usage logs.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Hermes Toolkit {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show", help="Show current Hermes settings")
    sub.add_parser("status", help="Show settings and recent usage summary")
    sub.add_parser("logs", help="Show recent API token usage logs")
    sub.add_parser("doctor", help="Check configuration for common issues")

    web = sub.add_parser("web", help="Run local web dashboard")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8088)

    profile = sub.add_parser("profile", help="Apply a settings profile")
    profile.add_argument("name", choices=["low-cost", "balanced", "premium"])

    model = sub.add_parser("model", help="Switch model/provider")
    model.add_argument("name", choices=["qwen", "gemini", "gpt"])

    set_cmd = sub.add_parser("set", help="Set a config value by dotted path")
    set_cmd.add_argument("key")
    set_cmd.add_argument("value")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    cfg = load_config()

    if args.command == "show":
        show(cfg)

    elif args.command == "status":
        status(cfg)

    elif args.command == "logs":
        print_logs()

    elif args.command == "doctor":
        doctor(cfg)

    elif args.command == "web":
        import uvicorn
        uvicorn.run("toolkit.web:app", host=args.host, port=args.port, reload=False)

    elif args.command == "profile":
        apply_profile(cfg, args.name, set_path)
        save_config(cfg)

    elif args.command == "model":
        apply_model(cfg, args.name, set_path)
        save_config(cfg)

    elif args.command == "set":
        path = tuple(args.key.split("."))
        value = parse_value(args.value)
        set_path(cfg, path, value)
        save_config(cfg)


if __name__ == "__main__":
    main()
