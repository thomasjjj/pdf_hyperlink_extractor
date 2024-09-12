import re
import streamlit as st
from docx import Document
from PyPDF2 import PdfReader

# Define a URL pattern to match hyperlinks
url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Function to extract links from PDFs
def extract_pdf_links(file):
    pdf_file = PdfReader(file)
    links = []
    for page_num in range(len(pdf_file.pages)):
        page = pdf_file.pages[page_num]
        if '/Annots' in page:
            annotations = page['/Annots']
            for annotation in annotations:
                a_entry = annotation.get_object().get('/A')
                if isinstance(a_entry, dict):
                    uri = a_entry.get('/URI')
                    if uri:
                        links.append(uri)
    return links

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
        links.extend(re.findall(url_pattern, para.text))
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
