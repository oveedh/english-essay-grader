import streamlit as st
import PyPDF2
from openai import OpenAI
#from unstructured.partition.pdf import partition_pdf
import pdf2image
from langchain_community.document_loaders import UnstructuredFileLoader

#elements = partition_pdf(filename=“…”)

client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def rubric_essay(rubric):
  prompt = f'''
  Given the rubric {rubric}
  Please provide a set of rules to evaluate the essays
   '''
  response = client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[{"role": 'user', "content":prompt}]
  )
  message = response.choices[0].message.content
  st.write(response)
  return message


def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text


st.markdown("# Upload rubric: PDF")
uploaded_rubric=st.file_uploader("Upload rubric",type="pdf")
if uploaded_rubric is not None:
    rubric_text = pdf_to_text(uploaded_rubric)
    #with open('rubric.pdf', 'wb') as f: 
    #    f.write(uploaded_rubric)
    loader = UnstructuredFileLoader(uploaded_rubric.readlines)
    loader.load()
    rules = rubric_essay(rubric_text)
    st.write('# llm_response')
    st.write(rules) 
    with st.expander("rubric"):
        st.write(f"{rubric_text}")

