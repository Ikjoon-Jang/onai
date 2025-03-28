import streamlit as st
import time
import os
from dotenv import load_dotenv
from aiqa.rag_query import generate_answer
from embedding.faiss_store import load_index_and_metadata

# 📦 .env 불러오기
load_dotenv()
FAISS_REFRESH_INTERVAL = int(os.getenv("FAISS_REFRESH_INTERVAL", 60))

# 📁 초기 로드: 세션에 저장
if "faiss_index" not in st.session_state or "faiss_meta" not in st.session_state:
    index, metadata = load_index_and_metadata()
    st.session_state["faiss_index"] = index
    st.session_state["faiss_meta"] = metadata
    st.session_state["last_refresh"] = time.time()

# ⏱ 갱신 로직
def should_refresh_index():
    return time.time() - st.session_state["last_refresh"] > FAISS_REFRESH_INTERVAL

if should_refresh_index():
    index, metadata = load_index_and_metadata()
    st.session_state["faiss_index"] = index
    st.session_state["faiss_meta"] = metadata
    st.session_state["last_refresh"] = time.time()

# 🖥️ UI 구성
st.set_page_config(page_title="Ontology RAG QA", page_icon="📦")
st.title("📦 온톨로지 기반 RAG 질의응답")

user_input = st.text_input("🗣️ 질문을 입력하세요", placeholder="예: 롱비치항의 위도는 얼마인가요?")

# 🤖 GPT 응답
if user_input:
    with st.spinner("🤖 GPT가 답변을 생성 중입니다..."):
        answer = generate_answer(
            user_input,
            st.session_state["faiss_index"],
            st.session_state["faiss_meta"]
        )
        st.markdown("### 🤖 GPT 응답")
        st.success(answer)

# 📊 벡터 상태 정보 (Sidebar)
with st.sidebar:
    st.header("📊 FAISS 상태")
    index = st.session_state["faiss_index"]
    metadata = st.session_state["faiss_meta"]
    st.markdown(f"**총 벡터 수**: `{index.ntotal}`")
    st.markdown("---")
    st.subheader("🧾 최근 등록 문장")
    if metadata:
        for i, text in enumerate(metadata[-3:][::-1]):
            st.markdown(f"**#{index.ntotal - i}**: {text[:100]}...")
    else:
        st.markdown("등록된 문장이 없습니다.")
