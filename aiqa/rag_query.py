# rag_query.py

from embedding.embedding import get_embedding
from embedding.faiss_store import search_faiss, load_index_and_metadata
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
GPT_MODEL = "gpt-3.5-turbo"

# GPT 응답 생성 함수
def generate_answer(user_question: str, index=None, metadata=None, top_k: int = 5) -> str:
    # 1. 사용자 질문 임베딩
    query_vec = get_embedding(user_question)

    # 2. 인덱스/메타데이터가 없으면 자동 로딩
    if index is None or metadata is None:
        index, metadata = load_index_and_metadata()

    # 3. FAISS 검색
    context_sentences = search_faiss(query_vec, index, metadata, top_k)
    context = "\n".join(context_sentences)

    # 4. GPT 질의
    messages = [
        {
            "role": "system",
            "content": "You are an expert AI assistant that uses domain knowledge to answer questions based on the provided context.",
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {user_question}",
        },
    ]

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
