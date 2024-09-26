import requests
import json
import streamlit as st
from datetime import datetime, timedelta

# API 키 설정
naver_client_id = st.secrets["NAVER_CLIENT_ID"]
naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
together_ai_api_key = st.secrets["TOGETHER_AI_API_KEY"]

def naver_search(query):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {
        "query": query,
        "display": 5,
        "sort": "date"  # 최신 뉴스부터 정렬
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 호출 중 오류 발생: {e}")
        return None

def together_ai_model(prompt):
    url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_ai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-Vision-Free",
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

def validate_and_summarize(query, news_data):
    if not news_data or 'items' not in news_data:
        return "검색 결과가 없습니다."

    # 최신성 검증
    current_date = datetime.now()
    recent_news = [item for item in news_data['items'] if (current_date - datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S +0900")).days <= 300]

    if not recent_news:
        return "최근 300일 이내의 관련 뉴스가 없습니다."

    # 뉴스 내용 요약
    news_text = "\n".join([f"{item['title']}: {item['description']}" for item in recent_news])
    prompt = f"""다음은 '{query}'에 대한 최근 뉴스 검색 결과입니다:

{news_text}

이 정보를 바탕으로 다음 작업을 수행해주세요:
1. '{query}'에 대해 간단히 요약해주세요.
2. 이 정보의 신뢰성을 평가해주세요. 정보가 일관적인지, 출처가 신뢰할 만한지 등을 고려해주세요.
3. 이 정보가 최신의 것인지 확인해주세요.
4. 추가 조사가 필요한 부분이 있다면 제안해주세요."""

    return together_ai_model(prompt)

def main():
    st.title("AI 기반 뉴스 검색 및 분석 시스템")
    
    query = st.text_input("검색어를 입력하세요")
    
    if st.button("검색 및 분석"):
        with st.spinner("검색 중..."):
            news_data = naver_search(query)
        
        with st.spinner("AI가 분석 중..."):
            analysis = validate_and_summarize(query, news_data)
        
        st.subheader("AI 분석 결과")
        st.write(analysis)

        st.subheader("참고한 뉴스 기사")
        if news_data and 'items' in news_data:
            for item in news_data['items']:
                st.markdown(f"[{item['title']}]({item['link']})")
                st.write(f"발행일: {item['pubDate']}")
                st.write("---")

if __name__ == "__main__":
    main()
