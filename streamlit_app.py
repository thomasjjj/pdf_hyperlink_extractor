import streamlit as st
from docx import Document

from pdf_extractor import URL_PATTERN, extract_pdf_links

# Function to extract links from DOCX files
def extract_docx_links(file):
    doc = Document(file)
    links = []
    for rel in doc.part.rels.values():
        if "hyperlink" in rel.reltype:
            url = rel._target
            if url:
                links.append(url)
    for para in doc.paragraphs:
        links.extend(URL_PATTERN.findall(para.text))
    return links

# Streamlit app UI
def main():
    st.title("Document Link Extractor")
    st.write("Upload a PDF or DOCX file, and this tool will retrieve all the hyperlinks.")

    # File uploader for PDF or DOCX
    uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=['pdf', 'docx'])
    
    if uploaded_file is not None:
        # Check file extension and extract links accordingly
        if uploaded_file.name.endswith('.pdf'):
            try:
                links = extract_pdf_links(uploaded_file)
            except ValueError as exc:
                st.error(str(exc))
                return
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
