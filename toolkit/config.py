from pathlib import Path
from datetime import datetime
import shutil
import yaml

CONFIG = Path("/root/.hermes/config.yaml")
LOG = Path("/root/.hermes/logs/agent.log")

def die(msg):
    raise SystemExit(f"ERROR: {msg}")

def load_config():
    if not CONFIG.exists():
        die(f"Config not found: {CONFIG}")
    return yaml.safe_load(CONFIG.read_text())

def backup_config():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = CONFIG.with_name(f"config.yaml.bak.hermes-toolkit.{ts}")
    shutil.copy2(CONFIG, dst)
    return dst

def save_config(cfg):
    cfg.get("session_reset", {}).pop("idle", None)
    backup = backup_config()
    CONFIG.write_text(yaml.safe_dump(cfg, sort_keys=False))
    print(f"Saved config. Backup: {backup}")

def get_path(cfg, path, default=None):
    node = cfg
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node

def set_path(cfg, path, value):
    node = cfg
    for key in path[:-1]:
        node = node.setdefault(key, {})
    old = node.get(path[-1])
    node[path[-1]] = value
    print(f"{'.'.join(path)}: {old!r} -> {value!r}")

def parse_value(raw):
    low = raw.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("none", "null"):
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw
