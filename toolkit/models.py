MODELS = {
    "qwen": ("openrouter", "qwen/qwen3-coder", None),
    "gemini": ("openrouter", "google/gemini-2.5-pro", None),
    "gpt": ("openai-codex", "gpt-5.5", None),
}

def apply_model(cfg, name, set_path):
    if name not in MODELS:
        raise SystemExit("Unknown model. Use: qwen, gemini, gpt")
    provider, model, base_url = MODELS[name]
    set_path(cfg, ("model", "provider"), provider)
    set_path(cfg, ("model", "default"), model)
    set_path(cfg, ("model", "base_url"), base_url)
