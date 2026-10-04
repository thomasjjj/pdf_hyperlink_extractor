"""Check pip and uv wheel installations outside the source checkout."""

import argparse
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from time import monotonic, sleep
from urllib.error import URLError
from urllib.request import urlopen
from zipfile import ZipFile

from tests.document_builders import build_pdf, build_sample_docx_bytes

CORE_CHECK = """
import importlib.util
import sys
from pathlib import Path
import pdf_hyperlink_extractor as package
from pdf_hyperlink_extractor import (
    DocumentSource, ExtractionError, PdfPasswordError,
    extract_links, extract_pdf_links, extract_docx_links,
)
assert Path(package.__file__).is_relative_to(Path(sys.prefix)), package.__file__
assert importlib.util.find_spec('streamlit') is None
assert 'streamlit' not in sys.modules
assert extract_links('sample.pdf', password='secret') == ['https://example.com']
assert extract_links(Path('sample.docx')) == ['https://example.com', 'https://example.org']
assert extract_pdf_links(Path('sample.pdf').read_bytes(), password='secret') == ['https://example.com']
with open('sample.docx', 'rb') as stream:
    stream.seek(5)
    assert extract_docx_links(stream) == ['https://example.com', 'https://example.org']
    assert stream.tell() == 5 and not stream.closed
try:
    extract_links('sample.pdf', password='wrong')
except PdfPasswordError as error:
    assert isinstance(error, ExtractionError)
else:
    raise AssertionError('Incorrect password was accepted')
assert 'streamlit' not in sys.modules
print('Installed core API extracts PDF/DOCX without Streamlit')
"""

UI_CHECK = """
from pathlib import Path
from streamlit.testing.v1 import AppTest
from pdf_hyperlink_extractor import streamlit_app
app = AppTest.from_file(streamlit_app.__file__).run()
assert not app.exception
assert app.button[0].disabled
data = Path('sample.docx').read_bytes()
mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
app.file_uploader[0].set_value(('sample.docx', data, mime)).run()
app.button[0].click().run()
assert not app.exception
assert app.code[0].value == 'https://example.com\\nhttps://example.org'
assert app.download_button[0].proto.ignore_rerun
print('Installed Streamlit app extracts uploaded documents')
"""


def _run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True, timeout=600)


def _check_wheel(wheel: Path) -> None:
    with ZipFile(wheel) as archive:
        names = archive.namelist()
    assert "pdf_hyperlink_extractor/py.typed" in names
    assert "pdf_hyperlink_extractor/streamlit_app.py" in names
    assert "pdf_hyperlink_extractor/ui.py" in names
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)
    assert all(
        name.startswith("pdf_hyperlink_extractor/") or ".dist-info/" in name for name in names
    ), names


def _check_server(launcher: Path, cwd: Path, env: dict[str, str]) -> None:
    with socket.socket() as address:
        address.bind(("127.0.0.1", 0))
        port = address.getsockname()[1]
    with (cwd / "server.log").open("w", encoding="utf-8") as log:
        server = subprocess.Popen(
            [
                str(launcher),
                "--server.headless=true",
                "--server.address=127.0.0.1",
                f"--server.port={port}",
                "--browser.gatherUsageStats=false",
                "--server.fileWatcherType=none",
            ],
            cwd=cwd,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = monotonic() + 45
            while monotonic() < deadline:
                if server.poll() is not None:
                    raise RuntimeError("Streamlit launcher exited before becoming healthy")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            print(
                                "Installed UI launcher responds on the requested port", flush=True
                            )
                            return
                except (URLError, TimeoutError):
                    sleep(0.2)
            raise RuntimeError("Streamlit launcher did not become healthy within 45 seconds")
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=10)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "distribution", type=Path, help="wheel file or directory containing one wheel"
    )
    options = parser.parse_args()
    wheel = options.distribution.resolve(strict=True)
    if wheel.is_dir():
        wheels = list(wheel.glob("*.whl"))
        if len(wheels) != 1:
            parser.error("the distribution directory must contain exactly one wheel")
        wheel = wheels[0]
    _check_wheel(wheel)
    uv = shutil.which("uv")
    if uv is None:
        parser.error("uv must be installed to verify both installers")
    env = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
        env.pop(variable, None)
    with tempfile.TemporaryDirectory(prefix="pdf-hyperlink-extractor-install-") as directory:
        workspace = Path(directory)
        (workspace / "sample.pdf").write_bytes(build_pdf("https://example.com", password="secret"))
        (workspace / "sample.docx").write_bytes(build_sample_docx_bytes())
        for installer in ("pip", "uv"):
            print(f"Checking {installer} base and Streamlit installations", flush=True)
            environment = workspace / installer
            _run([sys.executable, "-m", "venv", str(environment)], workspace, env)
            binary = environment / ("Scripts" if os.name == "nt" else "bin")
            python = binary / ("python.exe" if os.name == "nt" else "python")
            launcher = binary / (
                "pdf-hyperlink-extractor-ui.exe"
                if os.name == "nt"
                else "pdf-hyperlink-extractor-ui"
            )
            install = (
                [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--quiet"]
                if installer == "pip"
                else [uv, "pip", "install", "--quiet", "--python", str(python)]
            )
            _run([*install, str(wheel)], workspace, env)
            _run([str(python), "-I", "-c", CORE_CHECK], workspace, env)
            missing_extra = subprocess.run(
                [str(launcher)], cwd=workspace, env=env, capture_output=True, text=True, timeout=30
            )
            assert missing_extra.returncode != 0
            assert "uv sync --extra streamlit" in missing_extra.stderr, missing_extra.stderr
            _run([*install, f"{wheel}[streamlit]"], workspace, env)
            _run([str(python), "-I", "-c", UI_CHECK], workspace, env)
            _check_server(launcher, workspace, env)
    print("Wheel installation checks passed for pip and uv", flush=True)


if __name__ == "__main__":
    main()
