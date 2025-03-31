from embedding.embedding import get_embedding
from embedding.faiss_store import search_faiss, load_index_and_metadata
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
import logging

load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
GPT_MODEL = "gpt-3.5-turbo"

# GPT 응답 생성 함수
def generate_answer(user_question: str, index=None, metadata=None, top_k: int = 10) -> str:
    try:
        # 1. 사용자 질문 임베딩
        query_vec = get_embedding(user_question)

        # 2. 인덱스/메타데이터 자동 로딩
        if index is None or metadata is None:
            index, metadata = load_index_and_metadata()

        # 3. FAISS 검색
        results = search_faiss(query_vec, index, metadata, k=top_k)

        if not results:
            return "❗ 관련 정보를 찾을 수 없습니다. 질문을 다시 입력해 주세요."

        # 4. 유사도 포함 context 구성
        context_sentences = [f"[{score:.4f}] {text}" for text, score in results]
        context = "\n".join(context_sentences)

        # 🔍 DEBUG 출력
        print("\n📌 검색된 컨텍스트:")
        for i, (text, score) in enumerate(results, 1):
            print(f"[{i}] ({score:.4f}) {text[:80]}...")

        # 5. GPT 질의
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI assistant that uses domain knowledge to answer questions based on the provided context. "
                    "Answer accurately and concisely. If the context is insufficient, respond that the information is not available."
                )
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

    except Exception as e:
        logging.error(f"❌ GPT 응답 생성 오류: {e}")
        return f"❗ GPT 응답 생성 중 오류가 발생했습니다: {e}"
