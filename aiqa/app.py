import streamlit as st
from aiqa.rag_query import generate_answer

st.set_page_config(page_title="Ontology RAG QA", page_icon="🧠")
st.title("📦 온톨로지 기반 RAG 질의응답")

user_input = st.text_input("🗣️ 질문을 입력하세요", placeholder="예: 수출업체는 어떤 조건에서 운송을 담당하나요?")

if user_input:
    with st.spinner("🧠 GPT가 답변을 생성 중입니다..."):
        answer = generate_answer(user_input)
    st.markdown("### 🤖 GPT 응답")
    st.success(answer)