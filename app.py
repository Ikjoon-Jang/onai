import streamlit as st
from aiqa.rag_query import generate_answer
from dotenv import load_dotenv
import os
import time

load_dotenv()

REFRESH_INTERVAL = int(os.getenv("FAISS_REFRESH_INTERVAL", 60))  # 초 단위

# FAISS 인덱스 자동 리로드
def should_refresh_index():
    now = time.time()
    last = st.session_state.get("last_faiss_load", 0)
    return (now - last) > REFRESH_INTERVAL

# 인덱스 & 메타데이터 주기적 로딩
if should_refresh_index():
    from embedding.faiss_store import load_index_and_metadata
    st.session_state["faiss_index"], st.session_state["faiss_meta"] = load_index_and_metadata()
    st.session_state["last_faiss_load"] = time.time()

st.set_page_config(page_title="Ontology RAG QA", page_icon="📦")
st.title("📦 온톨로지 기반 RAG 질의응답")

user_input = st.text_input("🗣 질문을 입력하세요", placeholder="예: 롱비치항은 어디에 위치하나요?")

if user_input:
    with st.spinner("💭 GPT가 답변을 생성 중입니다..."):
        answer = generate_answer(user_input, st.session_state["faiss_index"], st.session_state["faiss_meta"])
        st.markdown("#### 🤖 GPT 응답")
        st.success(answer)
