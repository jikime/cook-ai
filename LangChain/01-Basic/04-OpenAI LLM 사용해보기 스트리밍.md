환경 변수를 안전하게 관리하고 싶으신가요? OpenAI의 최신 챗봇 모델을 활용하는 방법에 대해 알아보세요. 이 글에서는 `.env` 파일과 `gpt-3.5-turbo` 모델을 사용하는 실용적인 예제를 제공합니다.


**주요내용**
- 🔒 `.env` 파일을 사용해 중요 정보를 안전하게 관리하는 방법
- 🤖 OpenAI `gpt-3.5-turbo` 모델을 활용하여 챗봇을 만드는 과정
- ⚙️ `ChatOpenAI` 클래스와 `llm.stream` 메소드를 통한 실시간 AI 응답 구현

`dotenv` 라이브러리를 사용하여 `.env` 파일로부터 환경 변수를 로드한다. 이를 통해 API 키와 같은 중요한 정보를 코드에 직접 하드코딩하지 않고 안전하게 관리할 수 있다. `load_dotenv` 함수는 `.env` 파일에서 환경 변수를 읽어와 현재 환경에 로드한다.



```python
from dotenv import load_dotenv

# .env로부터 API KEY 정보 가져오기
load_dotenv()
```

이 예제는 `langchain_openai` 라이브러리를 사용하여 OpenAI의 챗봇 모델인 `gpt-3.5-turbo`를 활용하는 방법을 보여줍니다. `ChatOpenAI` 클래스를 사용하여 LLM(대규모 언어 모델) 객체를 생성하고, 이를 통해 사용자의 질문에 대한 실시간 응답을 받아옵니다. 생성된 LLM 객체는 `temperature`와 `max_tokens` 파라미터를 통해 응답의 창의성과 길이를 조절할 수 있습니다. 이 코드는 특정 질문(`"대한민국의 꽃은 무엇인가요?"`)에 대한 답변을 실시간으로 얻기 위해 `llm.stream` 메소드를 사용합니다.



```python
from langchain_openai import ChatOpenAI

# OpenAI Chat 전용 LLM 객체 생성
llm = ChatOpenAI(
    temperature=0.1,  # 창의성을 결정하는 값 (0.0 ~ 2.0 사이)
    max_tokens=2048,  # 채팅 결과로 생성되는 토큰의 최대 개수
    model_name="gpt-3.5-turbo",  # 사용할 모델의 이름
)

# 질의 내용
question = "대한민국의 꽃은 무엇인가요?"

# 질의 내용을 OpenAI Chat에 전달하고 결과를 실시간으로 받아온다.
results = llm.stream(question)
```

이 함수는 `results` 리스트를 순회하며 각 `result`의 `content` 속성을 실시간으로 출력합니다. 출력 시, 각 결과는 새 줄 없이 이어서 출력되며, `flush=True` 옵션을 사용하여 버퍼링 없이 즉시 출력됩니다.



```python
# 결과를 실시간으로 출력한다.
for result in results:
  print(result.content, end="", flush=True)
```
