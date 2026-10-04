"""Streamlit interface for document link extraction."""

from pathlib import Path

import streamlit as st

# Keep the original imports available for callers of earlier app versions.
from extractors import ExtractionError, extract_docx_links, extract_links, extract_pdf_links

__all__ = ["main", "extract_docx_links", "extract_pdf_links"]


def _clear_upload_state() -> None:
    st.session_state.pop("extraction_result", None)
    st.session_state.pop("pdf_password", None)


def main() -> None:
    """Extract once on request and retain results only for the current session."""
    st.set_page_config(page_title="Document Link Extractor", page_icon="🔗")
    st.title("Document Link Extractor")
    st.write("Extract hyperlinks and text links from a PDF or Word document.")
    st.caption("Supports web, mailto, and FTP links. Documents are processed in memory.")

    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        key="document",
        on_change=_clear_upload_state,
    )
    is_pdf = uploaded_file is not None and Path(uploaded_file.name).suffix.lower() == ".pdf"
    password = ""
    with st.form("extraction_options"):
        if is_pdf:
            password = st.text_input(
                "PDF password (optional)",
                type="password",
                key="pdf_password",
                help="Leave blank for PDFs that do not require a password.",
            )
        submitted = st.form_submit_button(
            "Extract links",
            type="primary",
            disabled=uploaded_file is None,
        )

    if submitted and uploaded_file is not None:
        st.session_state.pop("extraction_result", None)
        try:
            with st.spinner("Extracting links…"):
                links = extract_links(
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                    password=password,
                )
        except ExtractionError as exc:
            st.error(str(exc))
        else:
            st.session_state["extraction_result"] = (uploaded_file.name, links)

    result = st.session_state.get("extraction_result")
    if result is None:
        return
    filename, links = result
    if not links:
        st.info("No links found in the document.")
        if Path(filename).suffix.lower() == ".pdf":
            st.caption("Scanned PDF images need OCR before text links can be detected.")
        return

    st.success(f"Found {len(links)} unique {'link' if len(links) == 1 else 'links'}.")
    st.caption(f"Results for {filename}")
    link_text = "\n".join(links)
    st.code(link_text, language=None, wrap_lines=True)
    st.download_button(
        "Download links as text",
        link_text,
        file_name=f"{Path(filename).stem}_links.txt",
        mime="text/plain; charset=utf-8",
        on_click="ignore",
    )


if __name__ == "__main__":
    main()
