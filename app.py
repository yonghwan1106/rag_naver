import streamlit as st
import requests
from anthropic import Anthropic

# Streamlit secrets에서 API 키 가져오기
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# 네이버 뉴스 검색 함수
@st.cache_data(ttl=3600)
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
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"네이버 API 요청 중 오류 발생: {str(e)}")
        return None

# 검색 결과 처리 함수
def process_results(results):
    if not results or 'items' not in results:
        return "검색 결과가 없습니다."
    processed = []
    for item in results['items']:
        processed.append(f"제목: {item['title']}\n요약: {item['description']}\n날짜: {item['pubDate']}\n\n")
    return "".join(processed)

# Claude API를 사용한 텍스트 생성 함수
def generate_text(prompt):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Claude API 오류 발생: {str(e)}")
        return None

# RAG 시스템 함수
def rag_system(query):
    with st.spinner('검색 중...'):
        search_results = search_naver_news(query)
    
    if not search_results:
        return "뉴스 검색 중 오류가 발생했습니다."

    with st.spinner('정보 처리 중...'):
        processed_results = process_results(search_results)
    
    prompt = f"""다음은 네이버 뉴스 API를 통해 실시간으로 검색된 최신 뉴스 정보입니다. 
    이 정보를 바탕으로 질문에 답해주세요. 반드시 제공된 최신 뉴스 정보만을 사용하고, 
    귀하의 기존 지식은 사용하지 마세요.
    
    질문: {query}
    
    최신 뉴스 정보:
    {processed_results}
    
    위 최신 뉴스 정보만을 사용하여 답변해주세요:"""
    
    with st.spinner('답변 생성 중...'):
        response = generate_text(prompt)
        if response is None:
            return "답변을 생성하는 데 문제가 발생했습니다. 나중에 다시 시도해 주세요."
    
    return response

# Streamlit UI
st.title('AI 뉴스 어시스턴트')

user_query = st.text_input('질문을 입력하세요:', '최근 AI 기술의 발전 동향은?')

if st.button('답변 받기'):
    answer = rag_system(user_query)
    if answer:
        st.markdown(answer)

# 소스 표시
st.sidebar.title('정보')
st.sidebar.info('이 앱은 네이버 뉴스 API와 Anthropic의 Claude를 사용합니다.')
