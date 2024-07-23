**서버 실행**
uvicorn main:app --reload --port 8888

**클라이언트에서 API 요청**
http://localhost:8888/api/analyze

data = {
    "context": "여기에 분석할 텍스트 데이터를 넣습니다...",
    "question": "이 텍스트에 대한 질문을 여기에 넣습니다..."
}