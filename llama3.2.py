import requests
import json
import streamlit as st
from datetime import datetime, timedelta
import re

# API 키 설정
naver_client_id = st.secrets["NAVER_CLIENT_ID"]
naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
together_ai_api_key = st.secrets["TOGETHER_AI_API_KEY"]

# 신뢰할 수 있는 도메인 리스트
TRUSTED_DOMAINS = ['.gov', '.edu', 'naver.com', 'daum.net', 'chosun.com', 'donga.com', 'hani.co.kr']

# 네이버 통합검색 API
def naver_search(query):
    url = "https://openapi.naver.com/v1/search/webkr.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {
        "query": query,
        "display": 20,  # 결과 수를 20개로 증가
        "sort": "sim"   # 정확도순 정렬
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 호출 중 오류 발생: {e}")
        return None

# Together AI 모델 호출
def together_ai_model(prompt):
    url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_ai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        st.error(f"Together.ai API 호출 중 오류 발생: {e}")
        return None

# 검색 결과 필터링
def filter_search_results(search_data):
    if not search_data or 'items' not in search_data:
        return []
    
    filtered_items = []
    for item in search_data['items']:
        if any(domain in item['link'] for domain in TRUSTED_DOMAINS):
            filtered_items.append(item)
    
    return filtered_items[:10]  # 최대 10개 결과만 반환

# 소스 인용 포맷팅
def format_source_citation(item):
    return f"[{item['title']}]({item['link']}): \"{item['description']}\""

# 웹문서 결과를 처리
def validate_and_summarize(query, search_data):
    filtered_items = filter_search_results(search_data)
    if not filtered_items:
        return "신뢰할 수 있는 검색 결과가 없습니다."

    # 검색 결과 텍스트 생성
    search_text = "\n\n".join([format_source_citation(item) for item in filtered_items])

    prompt = f"""다음은 '{query}'에 대한 신뢰할 수 있는 웹 검색 결과입니다:

{search_text}

이 정보를 바탕으로 다음 작업을 수행해주세요:
1. '{query}'에 대해 간단히 요약해주세요. 반드시 각 정보의 출처를 명시하세요.
2. 이 정보의 신뢰성을 평가해주세요. 정보가 일관적인지, 출처가 신뢰할 만한지 등을 고려해주세요.
3. 이 정보가 최신의 것인지 확인해주세요. 정확한 날짜를 찾을 수 없다면, 내용을 바탕으로 추정해주세요.
4. 추가 조사가 필요한 부분이 있다면 제안해주세요.
5. 확실하지 않은 정보에 대해서는 반드시 "이 정보는 확실하지 않습니다" 또는 "추가 검증이 필요합니다"라고 명시해주세요.

답변 시 반드시 제공된 정보만을 사용하고, 추측이나 개인적인 의견은 피해주세요."""

    return together_ai_model(prompt)

# 메인 함수
def main():
    st.title("AI 기반 네이버 통합 검색 및 분석 시스템")
    
    query = st.text_input("검색어를 입력하세요")
    
    if st.button("검색 및 분석"):
        with st.spinner("검색 중..."):
            search_data = naver_search(query)
        
        with st.spinner("AI가 분석 중..."):
            analysis = validate_and_summarize(query, search_data)
        
        st.subheader("AI 분석 결과")
        st.write(analysis)
        
        st.subheader("참고한 검색 결과")
        filtered_items = filter_search_results(search_data)
        for item in filtered_items:
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write(item['description'])
            st.write("---")
        
        # 사용자 피드백 시스템
        feedback = st.radio("이 분석 결과가 도움이 되었나요?", ("매우 도움됨", "도움됨", "보통", "도움되지 않음", "매우 도움되지 않음"))
        if st.button("피드백 제출"):
            st.success("피드백이 제출되었습니다. 감사합니다!")

if __name__ == "__main__":
    main()
