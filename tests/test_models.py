from toolkit.models import apply_model


def test_apply_gpt_model():
    cfg = {"model": {"provider": "openrouter", "default": "openai/gpt-5.5"}}
    changes = []

    def set_path(cfg, path, value):
        node = cfg
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = value
        changes.append((path, value))

    apply_model(cfg, "gpt", set_path)

    assert cfg["model"]["provider"] == "openai-codex"
    assert cfg["model"]["default"] == "gpt-5.5"
    assert cfg["model"]["base_url"] is None
