import requests
import json
import streamlit as st
from datetime import datetime, timedelta

# API 키 설정
naver_client_id = st.secrets["NAVER_CLIENT_ID"]
naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
together_ai_api_key = st.secrets["TOGETHER_AI_API_KEY"]

# 네이버 통합검색 API
def naver_search(query):
    url = "https://openapi.naver.com/v1/search/webkr.json"  # 웹문서 검색 API
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {
        "query": query,
        "display": 10,  # 결과 수를 10개로 증가
        "sort": "sim"   # 정확도순 정렬
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 호출 중 오류 발생: {e}")
        return None

# 
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


# 웹문서 결과를 처리
def validate_and_summarize(query, search_data):
    if not search_data or 'items' not in search_data:
        return "검색 결과가 없습니다."

    # 검색 결과 텍스트 생성
    search_text = "\n".join([f"제목: {item['title']}\n설명: {item['description']}\n링크: {item['link']}" for item in search_data['items']])

    prompt = f"""다음은 '{query}'에 대한 네이버 웹 검색 결과입니다:

{search_text}

이 정보를 바탕으로 다음 작업을 수행해주세요:
1. '{query}'에 대해 간단히 요약해주세요.
2. 이 정보의 신뢰성을 평가해주세요. 정보가 일관적인지, 출처가 신뢰할 만한지 등을 고려해주세요.
3. 이 정보가 최신의 것인지 확인해주세요. (정확한 날짜 정보가 없을 수 있으므로, 내용을 바탕으로 판단해주세요)
4. 추가 조사가 필요한 부분이 있다면 제안해주세요."""

    return together_ai_model(prompt)

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
        if search_data and 'items' in search_data:
            for item in search_data['items']:
                st.markdown(f"[{item['title']}]({item['link']})")
                st.write(item['description'])
                st.write("---")

if __name__ == "__main__":
    main()
 
