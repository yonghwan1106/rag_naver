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
        "display": 5  # 결과 수를 5개로 제한
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
    url = "https://api.together.xyz/v1/chat/completions"
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
    st.title("뉴스 검색 및 요약 애플리케이션")
    
    query = st.text_input("검색어를 입력하세요")
    
    if st.button("검색"):
        # 네이버 검색 결과
        with st.spinner("네이버 검색 중..."):
            news_data = naver_search(query)
            if news_data and 'items' in news_data:
                st.subheader("네이버 검색 결과")
                for item in news_data['items']:
                    st.markdown(f"[**{item['title']}**]({item['link']})")
                    st.write(item['description'])
                    st.write("---")
            else:
                st.warning("검색 결과가 없습니다.")
        
        # LLM 요약 결과
        if news_data and 'items' in news_data:
            with st.spinner("LLM이 요약을 생성 중입니다..."):
                news_text = "\n".join([f"{item['title']}: {item['description']}" for item in news_data['items']])
                prompt = f"다음은 '{query}'에 대한 뉴스 검색 결과입니다:\n\n{news_text}\n\n이 정보를 바탕으로 '{query}'에 대해 간단히 요약해주세요."
                
                llm_response = together_ai_model(prompt)
                if llm_response:
                    st.subheader("LLM 요약 결과")
                    st.write(llm_response)
                else:
                    st.warning("LLM 요약을 생성하는데 실패했습니다.")

if __name__ == "__main__":
    main()
 
