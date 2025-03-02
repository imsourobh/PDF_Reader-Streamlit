from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 150

    def load_pdfs(self, file_paths):
        """Load multiple PDFs and return combined pages"""
        all_pages = []
        for file_path in file_paths:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            all_pages.extend(pages)
        return all_pages

    def split_into_chunks(self, pages):
        """Split pages into chunks"""
        text = "\n".join(page.page_content for page in pages)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        return splitter.split_text(text)