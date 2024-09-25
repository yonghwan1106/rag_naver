import streamlit as st
import requests
import json
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Streamlit secrets에서 API 키 가져오기
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# 네이버 뉴스 검색 함수
def search_naver_news(query, display=5):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 검색 결과 처리 함수
def process_results(results):
    processed = []
    for item in results['items']:
        processed.append(f"Title: {item['title']}\nDescription: {item['description']}\n")
    return "\n".join(processed)

# Claude API를 사용한 텍스트 생성 함수
def generate_text(prompt):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.completions.create(
            model="claude-3-sonnet-20240229",
            max_tokens_to_sample=300,
            prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
        )
        return response.completion
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# RAG 시스템 함수
def rag_system(query):
    with st.spinner('검색 중...'):
        search_results = search_naver_news(query)
    
    with st.spinner('정보 처리 중...'):
        processed_results = process_results(search_results)
    
    prompt = f"Query: {query}\nContext: {processed_results}\nAnswer:"
    
    with st.spinner('답변 생성 중...'):
        response = generate_text(prompt)
        if response is None:
            st.error("답변을 생성하는 데 문제가 발생했습니다. 나중에 다시 시도해 주세요.")
            return None
    
    return response



# Streamlit UI
st.title('AI 뉴스 어시스턴트')

user_query = st.text_input('질문을 입력하세요:', '최근 AI 기술의 발전 동향은?')

if st.button('답변 받기'):
    answer = rag_system(user_query)
    if answer:
        st.write(answer)

# 소스 표시
st.sidebar.title('정보')
st.sidebar.info('이 앱은 네이버 뉴스 API와 Anthropic의 Claude를 사용합니다.')
