import os
import streamlit as st
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from openai import OpenAI
import json

client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

import streamlit as st

from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from unstructured.staging.base import dict_to_elements

def process_file(file_contents, file_name):
    s=UnstructuredClient(api_key_auth=st.secrets['UNSTRUCTURED_API_KEY'])

    files=shared.Files(
        content=file_contents,
        file_name=file_name,
    )

    req = shared.PartitionParameters(
        files=files,
        strategy="hi_res",
        hi_res_model_name="yolox",
        skip_infer_table_types=[],
        pdf_infer_table_structure=True,
    )

    try:
        resp = s.general.partition(req)
        elements = dict_to_elements(resp.elements)
    except SDKError as e:
        print(e)

    tables = [el for el in elements]
    st.write("# START")
    final_text=""
    for t in tables:
        #table_html = t.metadata.text_as_html
        final_text += t.text
        #st.write(table_html)
    st.write("# COMPLETE")
    return resp, elements, tables, final_text

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

def analyze_paper(txt,col):
    with open("rubric.txt","r") as f:
        rubric_text=f.read()

    MESSAGE=[{"role": "user", 
                    "content": 
                    f'''
                    You are a high school english teacher, and you are responsible for grading students' essays. 
                    Analyze the following paper as per the rubric provided
                    You are helpful and generous and provide constructive feedback
                    Rubric is {rubric_text}
                    Essay is {txt}
                    provide the response as a JSON object

                    '''
                    }]
    response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=MESSAGE,
            response_format={ "type": "json_object" })
    json_response = response.choices[0].message.content
    json_analysis = json.loads(json_response)
    col.table(json_analysis)
    print(json_response)


st.markdown("# Upload paper: PDF")
uploaded_file=st.file_uploader("Upload paper",type="pdf")
col1, col2 = st.columns(2)

if uploaded_file is not None:
    file_content = uploaded_file.getbuffer()
    file_name = uploaded_file.name
    resp, elements, tables, final_text = process_file(file_content, file_name)
    #full_text = pdf_to_text(uploaded_file)
    with col1.expander("paper text"):
        st.write(final_text)
    analyze_paper(final_text,col2)
    #st.write(final_text)

   

