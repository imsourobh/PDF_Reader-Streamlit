import streamlit as st
import os
import asyncio
import time

from pdf_processor import PDFProcessor
from vector_db import VectorDBManager
from bot import QABot

class StreamlitApp:
    def __init__(self):
        # Initialize PDF processor and Vector DB manager
        self.pdf_processor = PDFProcessor()
        self.vector_db_manager = VectorDBManager()
        self.default_vector_db_path = r"A:\vscode\llm-pdf-reader\a_different_story"
        self.processed_pdfs = {}  # Track processed PDFs

    def setup_sidebar(self):
        # Setup sidebar for configuration options
        st.sidebar.header("PDF_Reader")
        option = st.sidebar.radio("Choose input method:", ("Upload PDFs", "Use Pre-trained Vector DB"))
        return option

    def handle_pdf_uploads(self):
        # Handle PDF uploads and processing
        uploaded_files = st.sidebar.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)
        db_name = st.sidebar.text_input("Name your Vector DB (optional)", value="combined_pdfs")
        
        if uploaded_files and st.sidebar.button("Process PDFs"):
            with st.spinner("Processing PDFs..."):
                # Initialize progress bar
                progress_bar = st.progress(0)
                total_steps = 4  # Save files, load PDFs, chunk, create vector DB
                current_step = 0

                # Step 1: Save uploaded files
                temp_file_paths = []
                new_files = []
                for uploaded_file in uploaded_files:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    temp_file_paths.append(temp_path)
                    if temp_path not in self.processed_pdfs:
                        new_files.append(temp_path)
                current_step += 1
                progress_bar.progress(int((current_step / total_steps) * 100))

                if new_files:
                    # Step 2: Load PDFs
                    pages = self.pdf_processor.load_pdfs(new_files)
                    current_step += 1
                    progress_bar.progress(int((current_step / total_steps) * 100))

                    # Step 3: Chunk PDFs
                    chunks = self.pdf_processor.split_into_chunks(pages)
                    current_step += 1
                    progress_bar.progress(int((current_step / total_steps) * 100))

                    # Delete temporary PDFs after chunking
                    for temp_path in temp_file_paths:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                    # Step 4: Create or update vector DB
                    save_path = db_name if db_name else self.vector_db_manager.default_save_path
                    if os.path.exists(save_path) and self.processed_pdfs:
                        vector_db = self.vector_db_manager.load_vector_db(save_path)
                        vector_db.add_texts(chunks)
                    else:
                        vector_db = self.vector_db_manager.create_vector_db(chunks, save_path)
                    st.session_state['bot'] = QABot(vector_db)
                    self.processed_pdfs.update({path: True for path in new_files})
                    current_step += 1
                    progress_bar.progress(int((current_step / total_steps) * 100))

                st.success(f"{len(new_files)} new PDFs processed, Vector DB saved as '{save_path}'!")

    def handle_vector_db_load(self):
        # Handle loading of pre-trained Vector DB
        st.sidebar.write("Please enter path manually, don't use quation sign. Remove them:(browing option will be added soon)")
        vector_db_path = st.sidebar.text_input("Enter Vector DB Path manually", value=self.default_vector_db_path)
        
        if st.sidebar.button("Load Vector DB"):
            with st.spinner("Loading Vector DB..."):
                try:
                    vector_db = self.vector_db_manager.load_vector_db(vector_db_path)
                    st.session_state['bot'] = QABot(vector_db)
                    st.success("Vector DB loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading Vector DB: {str(e)}")

    def display_chat_interface(self):
        # Display chat interface for user interaction
        st.header("Let's Chat here!")
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask your question here (type 'tata' to reset)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if 'bot' not in st.session_state or st.session_state.bot is None:
                with st.chat_message("assistant"):
                    message = "I'm requesting to activate me by loading your PDFs or load a Vector DB first. Only then ask me according to them! I can assist you after that.\n Please"
                    self.animate_text(message)
                    st.session_state.messages.append({"role": "assistant", "content": message})
            else:
                if prompt.lower() == "tata":
                    st.session_state.messages = []
                    st.success("Conversation reset!")
                else:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = st.session_state.bot.ask(prompt)
                            result = response["result"]
                        self.animate_text(result)
                        st.session_state.messages.append({"role": "assistant", "content": result})

    def animate_text(self, text, delay=0.1):
        """Display text word-by-word with a delay"""
        words = text.split()
        container = st.empty()
        displayed_text = ""
        
        for i, word in enumerate(words):
            displayed_text = " ".join(words[:i + 1])
            container.markdown(displayed_text)
            time.sleep(delay)

    def run(self):
        # Main entry point for the Streamlit app
        st.title("LLM-PDF-RERADER_IMSOUROBH")
        option = self.setup_sidebar()
        
        if option == "Upload PDFs":
            self.handle_pdf_uploads()
        else:
            self.handle_vector_db_load()
        
        self.display_chat_interface()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()