**주요내용**
- 🔒 `.env` 파일로 중요 정보 관리
- 🤖 멀티모달 `gpt-4o`와 `gpt-4-turbo` 모델 소개
- 🚀 `langchain_openai`와 `multimodal` 라이브러리를 사용한 AI 모델 초기화 및 스트리밍

`dotenv` 라이브러리를 사용하여 `.env` 파일로부터 환경 변수를 로드한다. 이를 통해 API 키와 같은 중요한 정보를 코드에 직접 하드코딩하지 않고 안전하게 관리할 수 있다.



```python
from dotenv import load_dotenv

# .env로부터 API KEY 정보 가져오기
load_dotenv()
```

멀티모달은 `텍스트, 이미지, 오디오, 비디오`를 통합하여 처리하는 기술이나 접근 방식입니다. `gpt-4o` 또는 `gpt-4-turbo` 모델은 이미지 인식 기능(vision)이 포함되어 있습니다.


이 코드는 `langchain_openai`와 `multimodal` 라이브러리를 사용하여 OpenAI의 챗봇 모델과 멀티모달 모델을 초기화합니다. `ChatOpenAI` 클래스를 사용하여 창의성을 조절할 수 있는 `temperature`, 생성될 토큰의 최대 개수를 지정하는 `max_tokens`, 그리고 사용할 모델명을 지정하는 `model_name`을 설정하여 LLM(Language Learning Model) 객체를 생성합니다. 이후, 생성된 LLM 객체를 `MultiModal` 클래스에 전달하여 멀티모달 객체를 생성합니다. 이 과정을 통해 텍스트 기반의 상호작용 뿐만 아니라 다양한 형태의 입력을 처리할 수 있는 AI 모델을 구성할 수 있습니다.



```python
from langchain_openai import ChatOpenAI
from multimodal import MultiModal

# OpenAI Chat 전용 LLM 객체 생성
llm = ChatOpenAI(
    temperature=0.1,  # 창의성 조절 (0.0 ~ 2.0 사이)
    max_tokens=2048,  # 채팅 결과로 생성되는 토큰의 최대 개수
    model_name="gpt-4o",  # 사용할 모델명
)

# 멀티모달 객체 생성
multimodal_llm = MultiModal(llm)
```

이 함수는 이미지 URL을 입력으로 받아 해당 이미지에 대한 설명을 생성합니다. `image_url` 변수에 이미지의 경로를 저장하고, `multimodal_llm.invoke` 함수를 호출하여 이미지 설명을 출력합니다.



```python
# 이미지 URL을 입력으로 받아, 이미지에 대한 설명을 생성하는 함수
image_url = "../../Assets/images/아름다운 무료 이미지.jpg"
print(multimodal_llm.invoke(image_url))
```

이 함수는 주어진 이미지 URL에서 멀티모달 LLM을 사용하여 스트리밍 결과를 실시간으로 출력합니다. 먼저, `image_url` 변수에 이미지의 URL을 할당합니다. 그 다음, `multimodal_llm.stream` 함수를 호출하여 해당 이미지 URL로부터 결과를 스트리밍합니다. 마지막으로, 결과의 내용(`content`)을 실시간으로 출력하기 위해 반복문을 사용합니다. 이 과정에서 `print` 함수는 `end=""` 옵션을 사용하여 출력 사이에 추가적인 줄바꿈 없이 연속적으로 결과를 출력하며, `flush=True` 옵션으로 버퍼링 없이 즉시 출력합니다.



```python
# 결과를 실시간으로 출력한다.
image_url = "https://plus.unsplash.com/premium_photo-1661914310117-9875b2229719?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
results = multimodal_llm.stream(image_url)

for result in results:
  print(result.content, end="", flush=True)
```
