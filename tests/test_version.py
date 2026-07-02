from pathlib import Path
from toolkit import __version__


def test_version_is_v07_alpha():
    assert __version__ == "0.7.0-alpha"


def test_sidebar_template_uses_app_version_global():
    template = Path("toolkit/templates/base.html").read_text()

    assert "v0.3-alpha" not in template
    assert "v{{ app_version }}" in template


def test_web_templates_expose_app_version():
    from toolkit.web import templates

    assert templates.env.globals["app_version"] == __version__
