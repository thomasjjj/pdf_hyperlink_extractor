"""Streamlit interface for extracting hyperlinks from documents."""

import streamlit as st

from extractors import extract_pdf_links, extract_docx_links


# Streamlit app UI
def main() -> None:
    """Run the Streamlit interface for hyperlink extraction."""
    st.title("Document Link Extractor")
    st.write("Upload a PDF or DOCX file, and this tool will retrieve all the hyperlinks.")

    # File uploader for PDF or DOCX
    uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=['pdf', 'docx'])

    if uploaded_file is not None:
        # Check file extension and extract links accordingly
        if uploaded_file.name.endswith('.pdf'):
            links = extract_pdf_links(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            links = extract_docx_links(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a PDF or DOCX file.")
            return

        # Display the extracted links
        if links:
            unique_links = list(set(links))  # Remove duplicates
            st.write("Extracted Links:")
            for link in unique_links:
                st.write(link)

            # Button to copy links to clipboard (Streamlit cannot access clipboard directly)
            st.download_button("Download Links as Text File", "\n".join(unique_links), file_name="extracted_links.txt")
        else:
            st.write("No links found in the document.")


if __name__ == "__main__":
    main()
