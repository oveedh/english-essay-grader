
from typing import Any

import numpy as np

import streamlit as st
from streamlit.hello.utils import show_code

#from utils import show_navigation
#show_navigation()


import os
import streamlit as st
from streamlit.logger import get_logger
import PyPDF2
from pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import hashlib
from openai import OpenAI

LOGGER = get_logger(__name__)

PINECONE_API_KEY=st.secrets['PINECONE_API_KEY']
PINECONE_API_ENV=st.secrets['PINECONE_API_ENV']
PINECONE_INDEX_NAME=st.secrets['PINECONE_INDEX_NAME']

client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"]) 

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

def embed(text,filename):
    #pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    index = pc.Index(PINECONE_INDEX_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap  = 200,length_function = len,is_separator_regex = False)
    docs=text_splitter.create_documents([text])
    for idx,d in enumerate(docs):
        hash=hashlib.md5(d.page_content.encode('utf-8')).hexdigest()
        embedding=client.embeddings.create(model="text-embedding-ada-002", input=d.page_content).data[0].embedding
        metadata={"hash":hash,"text":d.page_content,"index":idx,"model":"text-embedding-ada-003","docname":filename}
        index.upsert([(hash,embedding,metadata)])
    return

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
#
# Accept a PDF file using Streamlit
# Upload to Pinecone
#
st.markdown("# Upload paper: PDF")
uploaded_file=st.file_uploader("Upload paper",type="pdf")
if uploaded_file is not None:
    #pdf_text = pdf_to_text(uploaded_file)
    #embedding = embed(pdf_text,uploaded_file.name)
    file_contents = uploaded_file.getbuffer()
    with open("uploaded_paper.pdf", "wb") as f:
        f.write(file_contents)
   
    