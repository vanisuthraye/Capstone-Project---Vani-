Module 3 RAG Support Assistant
from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    import os
import chromadb

from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection("zepto_docs")

model = SentenceTransformer("all-MiniLM-L6-v2")

DOCS = "docs"

for file in os.listdir(DOCS):

    path = os.path.join(DOCS, file)

    text = open(path, encoding="utf-8").read()

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[file],
        documents=[text],
        embeddings=[embedding]
    )

print("Embedded successfully.")
python embed_documents.py
import chromadb

from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection("zepto_docs")

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query):

    emb = model.encode(query).tolist()

    result = collection.query(
        query_embeddings=[emb],
        n_results=3
    )

    return result
PROMPT = """
ROLE
You are Zepto Policy Assistant.

CONTEXT
{context}

TASK
Answer only using the provided context.

NEGATIVE CONSTRAINT
Do NOT answer using information not present in the context.

FORMAT
Provide a concise answer.

LENGTH
Maximum 120 words.

Few-shot Example

Question:
What is the refund policy?

Answer:
Refunds are processed within 3–5 business days to the original payment method or instantly to the Zepto wallet.
"""
import os

from groq import Groq

MOCK = os.getenv("MOCK_LLM", "1") != "0"


def classify(query):

    keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours"
    ]

    q = query.lower()

    if MOCK:

        if any(k in q for k in keywords):
            return "policy_question"

        return "general_question"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"Classify: {query}"

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )

    return res.choices[0].message.content.strip()
import os

from typing import TypedDict

from langgraph.graph import StateGraph, END

from retriever import retrieve
from llm import classify

MOCK = os.getenv("MOCK_LLM", "1") != "0"


class State(TypedDict):

    query: str

    intent: str

    answer: str

    sources: list

    confidence: float


def classify_node(state):

    state["intent"] = classify(state["query"])

    return state


def retrieve_node(state):

    result = retrieve(state["query"])

    docs = result["documents"][0]

    ids = result["ids"][0]

    if MOCK:

        snippet = docs[0][:200]

        answer = f"Based on the retrieved context: {snippet}"

    else:

        answer = "LLM generated answer"

    state["answer"] = answer

    state["sources"] = ids

    state["confidence"] = 1.0

    return state


def direct_node(state):

    if MOCK:

        answer = "I can only answer questions about Zepto policies right now."

    else:

        answer = "LLM general answer"

    state["answer"] = answer

    state["sources"] = []

    state["confidence"] = 1.0

    return state


graph = StateGraph(State)

graph.add_node("classify_intent", classify_node)

graph.add_node("retrieve_and_answer", retrieve_node)

graph.add_node("direct_answer", direct_node)

graph.set_entry_point("classify_intent")


graph.add_conditional_edges(

    "classify_intent",

    lambda s: s["intent"],

    {

        "policy_question": "retrieve_and_answer",

        "general_question": "direct_answer"

    }

)

graph.add_edge("retrieve_and_answer", END)

graph.add_edge("direct_answer", END)

app_graph = graph.compile()
from fastapi import FastAPI

from graph import app_graph

from models import QueryRequest, QueryResponse

app = FastAPI()


@app.post("/ask", response_model=QueryResponse)

def ask(req: QueryRequest):

    state = {

        "query": req.query,

        "intent": "",

        "answer": "",

        "sources": [],

        "confidence": 0

    }

    result = app_graph.invoke(state)

    return QueryResponse(

        answer=result["answer"],

        sources=result["sources"],

        confidence=result["confidence"]

    )
uvicorn main:app --reload
POST /ask

{
  "query":"What is the refund policy?"
}
{
  "answer":"Based on the retrieved context: Grocery and perishable items may be reported...",
  "sources":[
      "doc_02.txt",
      "doc_06.txt",
      "doc_05.txt"
  ],
  "confidence":1.0
}
{
    "query":"Who won IPL?"
}
{
    "answer":"I can only answer questions about Zepto policies right now.",
    "sources":[],
    "confidence":1.0
}
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","7860"]
docker build -t support_assistant .
docker run -p 7860:7860 support_assistant
