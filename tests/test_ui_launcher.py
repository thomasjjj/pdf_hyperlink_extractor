import builtins
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from pdf_hyperlink_extractor import ui


@pytest.mark.parametrize("missing", ["streamlit", "streamlit_dependency"])
def test_launcher_reports_missing_extra_without_hiding_other_import_errors(monkeypatch, missing):
    original = builtins.__import__

    def import_without_streamlit(name, *args, **kwargs):
        if name == "streamlit.web.cli":
            raise ModuleNotFoundError(f"No module named {missing!r}", name=missing)
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_streamlit)
    if missing == "streamlit":
        with pytest.raises(SystemExit, match="uv sync --extra streamlit"):
            ui.main()
    else:
        with pytest.raises(ModuleNotFoundError, match=missing):
            ui.main()


@pytest.mark.streamlit
def test_launcher_uses_packaged_app_and_forwards_server_arguments(monkeypatch):
    cli = pytest.importorskip("streamlit.web.cli")
    launch = Mock()
    monkeypatch.setattr(cli, "main", launch)
    monkeypatch.setattr(sys, "argv", ["pdf-hyperlink-extractor-ui", "--server.port", "8765"])
    ui.main()
    assert sys.argv == [
        "streamlit",
        "run",
        str(Path(ui.__file__).with_name("streamlit_app.py")),
        "--server.port",
        "8765",
    ]
    launch.assert_called_once_with()
