from openai import OpenAI
import os
import streamlit as st
import PyPDF2

avatars={"system":"💻🧠","user":"🧑‍💼","assistant":"🎓"}
client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

text_content = pdf_to_text("uploaded_paper.pdf")

with open("rubric.txt","r") as f:
    rubric_text=f.read()

SYSTEM_MESSAGE={"role": "system", 
                "content": 
                f'''
                You are a high school english teacher, and you are responsible for grading students' essays. 
                Analyze the following paper as per the rubric provided
                You are helpful and patient
                Rubric is {rubric_text}
                Essay is {text_content}
                Provide the response as a JSON object
                Provide a score per metric as per the rubric
                At the end, provide verbose feedback as a separate JSON element to improve the essay
                '''
                }
                
guide_format = '''
                critera: score: condition

                '''

example_rubric_write = '''
                        #Rubric is | | excellent | fair | poor |
                        #| topic sentence | original and powerful | clear thesis statement | Vague or missing thesis statement |
                        #should return 
                        #criteria_list = 
                        #topic sentence, excellent, orginal and powerful
                        #topic sentence, fair, clear thesis statement
                        #topic sentence, poor, Vague or missing thesis statement
                        #'''

#SYSTEM_MESSAGE={"role": "system", 
                #"content": 
                #'''
                #You are a high school curriculum creator and you are responsible for creating an essay evaluation guide
                #based on the rubric provided
                #Here is the format {guide_format}
                #Here is an example {example_rubric_write}

                #Rubric is {rubric_text}
                

                #'''
     #           }

user_message = {"role":"user",
               "content":"should return"
}



#st.sidebar.write(rubric_text)
#st.sidebar.write(text_content)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(SYSTEM_MESSAGE)

for message in st.session_state.messages:
    if message["role"] != "system":
        avatar=avatars[message["role"]]
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    prompt = "please analyze this essay"
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.sidebar.expander("llm_prompt"):
        for m in st.session_state.messages:
            roller = m["role"]
            msg = m["content"]
            st.write(f"{roller}:{msg}")

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        message_placeholder = st.empty()
        full_response = ""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages], 
            response_format={ "type": "json_object" })
        json_response = response.choices[0].message.content
        message_placeholder.markdown(json_response)
        st.session_state.messages.append({"role": "assistant", "content": json_response})