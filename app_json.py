import streamlit as st
import openai
import json
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 🔐 OpenAI API 키 설정 (환경 변수 사용 권장)
# openai.api_key = "sk-..."  # 실제 키로 교체하거나 환경변수로 설정

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="물류 추천 시스템", layout="centered")
st.title("🚚 물류 오더 추천 시스템")

st.markdown("""
신규 오더 정보(출발지, 도착지, 납기일)를 입력하면, 
기존 유사 오더 기반으로 운송 계획을 추천해줍니다.
""")

# 📥 사용자 입력
with st.form("order_form"):
    departure = st.text_input("출발지", placeholder="예: 서울")
    arrival = st.text_input("도착지", placeholder="예: 부산")
    due_date = st.date_input("납기일")
    submitted = st.form_submit_button("추천 요청")

# GPT Tool Schema 정의
tool_schema = [
    {
        "type": "function",
        "function": {
            "name": "recommend_logistics_plan",
            "description": "유사한 과거 오더 기반 물류 계획 추천",
            "parameters": {
                "type": "object",
                "properties": {
                    "estimated_departure_date": { "type": "string" },
                    "estimated_arrival_date": { "type": "string" },
                    "recommended_route": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "departure": { "type": "string" },
                                "arrival": { "type": "string" },
                                "carrier": { "type": "string" },
                                "duration_days": { "type": "number" },
                                "transport_cost": { "type": "number" },
                                "storage_cost": { "type": "number" }
                            }
                        }
                    },
                    "total_transport_cost": { "type": "number" },
                    "total_storage_cost": { "type": "number" }
                }
            }
        }
    }
]

if submitted:
    # 메시지 구성
    user_message = f"""
    출발지는 {departure}이고, 도착지는 {arrival}이야. 
    납기일은 {due_date.strftime('%Y-%m-%d')}인데, 언제 출발해야 할까? 
    어떤 운송사가 좋고, 예상 비용은 얼마야?
    """

    with st.spinner("OpenAI에게 물어보는 중..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "user", "content": user_message}],
                tools=tool_schema,
                tool_choice="auto"
            )

            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)

            st.success("✅ 추천 결과 도착!")

            st.subheader("📅 운송 일정")
            st.write(f"**출발 예정일:** {result['estimated_departure_date']}")
            st.write(f"**도착 예정일:** {result['estimated_arrival_date']}")

            st.subheader("🚛 추천 경로")
            for idx, route in enumerate(result['recommended_route'], 1):
                st.markdown(f"**구간 {idx}**")
                st.write(f"- 출발지: {route['departure']}")
                st.write(f"- 도착지: {route['arrival']}")
                st.write(f"- 운송사: {route['carrier']}")
                st.write(f"- 소요일: {route['duration_days']}일")
                st.write(f"- 운송비: {route['transport_cost']:,}원")
                st.write(f"- 보관비: {route['storage_cost']:,}원")

            st.subheader("💰 총 비용 예측")
            st.write(f"**총 운송비:** {result['total_transport_cost']:,}원")
            st.write(f"**총 보관비:** {result['total_storage_cost']:,}원")

        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")
