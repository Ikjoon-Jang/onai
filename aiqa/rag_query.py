# rag_query.py

from embedding.embedding import get_embedding
from embedding.faiss_store import search_faiss
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GPT_MODEL = "gpt-3.5-turbo"

def generate_answer(user_question: str, top_k: int = 5) -> str:
    # 1. 사용자 질문을 임베딩
    query_vec = get_embedding(user_question)

    # 2. FAISS에서 관련 문장 검색
    context_sentences = search_faiss(query_vec, k=top_k)
    context = "\n".join(context_sentences)

    # 3. GPT에 질의
    messages = [
        {"role": "system", "content": "You are an expert AI assistant that uses domain knowledge to answer questions based on the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_question}"}
    ]

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()