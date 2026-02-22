from ingestion import extract_text
from embeddings import create_embeddings, get_vector_store 
from config import model_name
from agent import QueryAgent_state, retrieve, generate
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Path, HTTPException
from langgraph.graph import StateGraph, START, END
import uvicorn
from pydantic import BaseModel, Field
from langchain_community.vectorstores import FAISS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tracks whether a document has been ingested
doc = None

@app.post("/upload")
async def upload(file: UploadFile):
    global doc
    try:
        text = extract_text(file)
        print(text)
        if not text.strip():
            doc = False
            raise HTTPException(status_code=400, detail="Document is empty.")
        print('Text Extracted !!!!!!!!!!!!!!!!')
        print(text[0])
        print(file.filename)
        
        chunks = create_embeddings(model_name, text, file.filename)

        if chunks:
            vector_store = get_vector_store()
            print('vector_store is ..........', vector_store)
            print(type(vector_store))
            faiss_indx_uplded_doc = vector_store.save_local("faiss_index")


        print('Chunks are created or not ..........')
        print(chunks)
        # mark document as ingested so `/query` knows data exists
        doc = True
        print('doc flag = True')
        print(f"Chunks created: {len(chunks)}")
        return {"status": "Successfully ingested data.", "message": f"Ingested {len(chunks),chunks} chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


builder = StateGraph(QueryAgent_state)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

rag_agent = builder.compile()

class query_request(BaseModel):
        query : str = Field(..., min_length=1)

@app.post('/query')
async def submit_query(queryy: query_request):
    if doc is None:  
        return {'answer':'No document uploaded!'}  
    
    result = rag_agent.invoke({'query':queryy.query})

    return {'answer':result['answer'], 'citation':result['citation']}  



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0',port=8000)