from langchain_ollama import OllamaLLM
from typing import TypedDict, Annotated, Optional
from embeddings import get_vector_store
from fastapi import FastAPI, Form, File, UploadFile
import json, ast, re
from config import llm_model

class QueryAgent_state(TypedDict):
    query : str
    context : Optional[str]
    answer : Optional[str]
    citation : Optional[str]  


def retrieve(state: QueryAgent_state):
    query = state["query"]
    vector_store = get_vector_store()
    if not vector_store:
        raise RuntimeError("Vector store not initialized. Upload and ingest a document first.")

    docs = vector_store.similarity_search(query, k=3)
    contexts = []
    for docs_chunk in docs:
        src = ""
        try:
            src = docs_chunk.metadata.get("source", "")
        except Exception:
            try:
                src = getattr(docs_chunk, "source", "")
            except Exception:
                src = ""
        print('src is .....', src)

        citation = f" Citation: \n\n Source: {src} \n\n Para: {docs_chunk.page_content}" if src else ""
        print('type of citation is ..........', type(citation))
        print('Citation is ..........', citation)
        print('-------------------')
        print('This is docs_chunk:  ', docs_chunk)
        print('-------------------')
        contexts.append(docs_chunk.page_content + citation)
        print('-------------------')

    return {"context": "\n\n".join(contexts), "citation": citation} 


def clean_json_response(raw_response: str):
        # This regex finds the content between the first { and the last }
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if match:
            return match.group(0)
        return raw_response

llm_model_name = llm_model

def generate(state: QueryAgent_state):
    llm = OllamaLLM(model=llm_model_name)
    cost_estimation_check_prompt = f'''
    ### Role
    You are an expert Intent Classification Agent. Your task is to analyze a User Query and determine if it is a request for a "Cost Estimation" regarding a service, product, or solution.

    ### Criteria for "Cost Estimation" (True):
    1.  **Direct Pricing:** Asking for a specific cost, price, or rate. (e.g., "How much is the license?")
    2.  **Budgetary Impact:** Asking about financial requirements. (e.g., "What's the budget for this?")
    3.  **Quotations:** Requesting a formal estimate or bid. (e.g., "Give me a quote for 100 users.")
    4.  **Resource/Time Costs:** Asking about expenses related to hours or labor. (e.g., "What are the billable hours for setup?")
    5.  **Comparative Costs:** Asking which option is more expensive.

    ### Criteria for "General Query" (False):
    1.  **Features/Technical:** "How does the API work?"
    2.  **Logistics:** "Where is your office located?"
    3.  **Support:** "How do I reset my password?"

    ### Output Format
    You must respond in the following JSON format:
    {{
    "is_cost_estimation": bool,
    "confidence_score": float (0.0 to 1.0),
    "reasoning": "A brief explanation of why this was or was not classified as cost estimation."
    }}

    ### User Query:
    "{state.get('query','')}"
    '''

    cost_estimation_check_response = llm.invoke(cost_estimation_check_prompt)

    
    print('===================================******++++++++++++++++++++++++++++++++++++')

    print('Raw cost_estimation_check_response is ..........', cost_estimation_check_response)
    cost_estimation_check_response = clean_json_response(cost_estimation_check_response)
    print('Cleaned cost_estimation_check_response is ..........', cost_estimation_check_response)
    print('===================================******++++++++++++++++++++++++++++++++++++')


    print('===================================******++++++++++++++++++++++++++++++++++++')
    print(type(cost_estimation_check_response))
    cost_estimation_check_response = cost_estimation_check_response.strip()
    print('===================================******++++++++++++++++++++++++++++++++++++')

    print(cost_estimation_check_response)  
    print('===================================******++++++++++++++++++++++++++++++++++++')
    cost_estimation_check_response = cost_estimation_check_response.lower().replace('false','False').replace('true','True')  # Remove 'false' and 'true' from the string
    print('===================================******++++++++++++++++++++++++++++++++++++')

    print(cost_estimation_check_response)
    print('===================================******++++++++++++++++++++++++++++++++++++')
    print('Converting to Dictionary...........')
    cost_estimation_check_response = ast.literal_eval(cost_estimation_check_response)  # Convert string to dictionary
    print(cost_estimation_check_response)

    print('===================================******++++++++++++++++++++++++++++++++++++')
    print(type(cost_estimation_check_response))
    print('===================================******++++++++++++++++++++++++++++++++++++')

    if cost_estimation_check_response.get('is_cost_estimation'):
        print('Cost Estimation Enquiry Detected. Invoking Cost Estimation Agent...')
        print('===================================******++++++++++++++++++++++++++++++++++++')

        cost_estimation_prompt = f'''
        ### Role
        You are a Financial Analyst Agent. Your task is to extract and calculate cost estimations strictly based on the provided Context.

        ### Task
        Analyze the Context to find any pricing, service fees, resource costs, or hardware/software expenses related to the User Query. 

        ### Instructions:
        1.  **Strict Context Adherence:** Only use information provided in the Context. If the price is not mentioned, state "Cost information not found in document."
        2.  **Itemization:** If multiple costs are mentioned, list them as bullet points.
        3.  **Total Calculation:** If the user asks for a total and the document provides individual rates (e.g., $50/hr for 10 hours), perform the calculation.
        4.  **Assumptions:** Clearly state any assumptions made (e.g., "Assuming standard tax rates as per page 3").
        5.  **Currency:** Maintain the currency format used in the document.

        ### Context:
        {state.get('context','')}

        ### User Query:
        {state.get('query','')}

        ### Response Format:
        - **Estimated Cost:** [Provide the specific number or range]
        - **Breakdown:** [Itemized list of what contributes to this cost]
        - **Confidence/Notes:** [Mention if the cost is fixed, estimated, or dependent on variables found in the text]
        '''
        cost_estimation_response = llm.invoke(cost_estimation_prompt)
        print('===================================******++++++++++++++++++++++++++++++++++++')
        print('type of cost_estimation_response....',type(cost_estimation_response))
        print('Cost Estimation Response is ..........', cost_estimation_response)
        combine_response = 'Checking for Cost Estimation Enquiry: \n\n' + str(cost_estimation_check_response) + '\n\n' + 'Answer' + '\n\n' + cost_estimation_response
        print('===================================******++++++++++++++++++++++++++++++++++++')
        print('combine_response is ..........', combine_response)
        
    else:
        prompt = f'''
        ### Role
        You are a Precise Information Extraction Agent. Your goal is to answer questions based ONLY on the provided Context.

        ### Constraints
        1. **Grounding:** Do not use any outside knowledge. Answer according to the information in the provided context.
        2. **No Hallucinations:** Never make up facts, dates, or prices.
        3. **Verbatim Phrases:** When possible, use the exact terminology or phrases found in the Context.

        ### Provided Context:
        {state.get('context','')}

        ### User Query:
        {state.get('query','')}

        ### Final Answer:
        '''

        response = llm.invoke(prompt)
        print('===================================******++++++++++++++++++++++++++++++++++++')
        print('type of response....',type(response))
        print('Response is ..........', response)
        combine_response = 'Checking for Cost Estimation Enquiry: \n\n' + str(cost_estimation_check_response) + '\n\n' + 'Answer' + '\n\n' + response
        print('combine_response is ..........', combine_response)

    return {'answer': combine_response}
