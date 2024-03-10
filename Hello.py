# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

import PyPDF2

client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def rubric_essay(rubric,essay):
  prompt = f'''
  Please evaluate the essay according to the rubric{rubric}
  Essay is {essay}
   '''
  for response in client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages], stream=True):

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    st.markdown("Upload rubric")
    rubric_text = st.text_area("Enter rubric","")

    st.markdown("# Upload essay: PDF")
    uploaded_file=st.file_uploader("Upload essay",type="pdf")
    if uploaded_file is not None:
        pdf_text = pdf_to_text(uploaded_file)
        with st.expander("rubric"):
          st.write(f"{rubric_text}")
        with st.expander("pdf text"):
          st.write(f"{pdf_text}")
        
        result=rubric_essay(rubric_text,pdf_text)

if __name__ == "__main__":
    run()

