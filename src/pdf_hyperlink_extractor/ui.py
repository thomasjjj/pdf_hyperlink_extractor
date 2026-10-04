"""Launch the optional Streamlit interface from an installed package."""

import sys
from pathlib import Path


def main() -> None:
    """Run the packaged app, forwarding arguments to the Streamlit CLI."""
    try:
        from streamlit.web.cli import main as streamlit_main
    except ModuleNotFoundError as exc:
        if exc.name != "streamlit":
            raise
        raise SystemExit(
            'The Streamlit interface requires the "streamlit" extra.\n'
            "Reinstall the package with its streamlit extra.\n"
            'From a source checkout: pip install ".[streamlit]" '
            "or uv sync --extra streamlit"
        ) from None

    app = Path(__file__).with_name("streamlit_app.py")
    sys.argv = ["streamlit", "run", str(app), *sys.argv[1:]]
    streamlit_main()


if __name__ == "__main__":
    main()
