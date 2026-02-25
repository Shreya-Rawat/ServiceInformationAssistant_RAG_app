from langchain_huggingface import data
import streamlit as st
import requests as re
from config import upload_file_url
from fastapi import FastAPI, Path, HTTPException



st.title('Service Information Assistant')

ur_file = st.file_uploader('Upload your text file here: ', type=['pdf','doc','docx'])

try:
    if ur_file:
        upload_file = {'file':(ur_file.name, ur_file.getvalue())}
        post_data_response = re.post(upload_file_url+'/upload', files = upload_file)
        st.success(post_data_response.json()["status"])
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


query = st.text_input("Ask a question about your document:")
if st.button("Ask") and query:
    with st.spinner("Thinking..."):
        res = re.post(f"{upload_file_url}/query", json={"query": query})
        st.write("### Answer:")

        data = res.json()
        answer = data.get("answer", "No answer found")
        citation = data.get("citation", "No citation available")

        st.write(answer)
        st.info(f"**Source:** {citation}")
        



