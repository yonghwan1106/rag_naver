import requests
import json
import streamlit as st

# API 키 설정
naver_client_id = st.secrets["NAVER_CLIENT_ID"]
naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
together_ai_api_key = st.secrets["TOGETHER_AI_API_KEY"]

# 네이버 API 연동
def naver_search(query):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {
        "query": query,
        "display": 10
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 호출 중 오류 발생: {e}")
        return None

# Together.ai API 연동
def together_ai_model(prompt):
    url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_ai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.2-90b-instruct",
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

# 데이터 처리
def process_data(data):
    if not data or 'items' not in data:
        return ""
    return "\n".join([item['title'] + ": " + item['description'] for item in data['items']])

# RAG 개발
def rag(query):
    news_data = naver_search(query)
    if not news_data:
        return "검색 결과를 가져오는 데 실패했습니다."
    
    processed_data = process_data(news_data)
    prompt = f"다음은 '{query}'에 대한 뉴스 검색 결과입니다:\n\n{processed_data}\n\n이 정보를 바탕으로 '{query}'에 대해 요약해주세요."
    
    response = together_ai_model(prompt)
    return response if response else "응답 생성에 실패했습니다."

# 스트림릿 클라우드 배포
def main():
    st.title("RAG 애플리케이션")
    query = st.text_input("질문 입력")
    if st.button("검색"):
        with st.spinner("응답을 생성 중입니다..."):
            response = rag(query)
            st.write(response)

if __name__ == "__main__":
    main()
