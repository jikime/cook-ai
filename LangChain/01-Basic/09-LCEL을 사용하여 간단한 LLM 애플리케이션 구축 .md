**주요내용**
- 📦 `python-dotenv`, `langchain` 등의 패키지 조용한 설치 방법
- 🌐 `.env` 파일로부터 환경 변수 로드 및 관리
- 🔗 LCEL을 사용한 LangChain 컴포넌트들의 chaining 기법 소개
- 🚀 FastAPI와 `uvicorn`을 활용한 API 서버 구축 및 실행 방법
- 🌍 다양한 언어로의 텍스트 번역 및 처리 기능 구현

`python-dotenv`, `langchain`, `langchain-cli`, `langchain-openai`, `langserve`, `uvicorn` 패키지들을 조용히 업데이트하며 설치하는 방법을 설명합니다. 사용자는 이 명령어를 실행하여 필요한 패키지들을 최신 버전으로 업데이트하고 설치할 수 있습니다. 이 과정은 출력을 최소화하여 진행됩니다.



```python
%pip install -qU python-dotenv langchain langchain-cli langchain-openai langserve uvicorn 
```

환경 변수를 관리하기 위해 `dotenv` 라이브러리를 사용합니다. 이는 `.env` 파일에서 정의된 환경 변수를 로드하여 프로그램에서 사용할 수 있게 해줍니다. `load_dotenv` 함수를 호출함으로써, `.env` 파일에 저장된 환경 변수들이 프로그램의 환경 변수로 로드됩니다.



```python
from dotenv import load_dotenv

load_dotenv()
```

아래 코드는 `langchain_openai` 라이브러리에서 `ChatOpenAI` 클래스를 임포트하여 사용합니다. `ChatOpenAI` 인스턴스를 생성할 때, `temperature`, `max_tokens`, 그리고 `model` 이름을 인자로 제공합니다. 여기서 `temperature`는 생성된 텍스트의 창의성을 조절하며, 낮은 값은 더 예측 가능한 텍스트를 생성합니다. `max_tokens`는 생성할 수 있는 최대 토큰 수를 정의하고, `model`은 사용할 모델의 이름을 지정합니다. 여기서는 `gpt-4o-mini` 모델을 사용합니다.



```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    temperature=0.1,  
    max_tokens=2048,  
    model="gpt-4o-mini",  
)
```

아래 코드는 `langchain_core.messages`에서 `HumanMessage`와 `SystemMessage` 클래스를 가져와 사용합니다. 먼저, 영어에서 한국어로 번역하라는 요청을 담은 `SystemMessage` 인스턴스와 사용자의 인사말을 담은 `HumanMessage` 인스턴스를 생성합니다. 이후, 이 메시지 리스트를 `model.invoke()` 함수에 전달하여 처리합니다. 이 과정은 시스템이 사용자의 요청을 이해하고 적절한 작업을 수행하기 위한 메시지 처리 절차를 보여줍니다.



```python
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="영어에서 한국어로 다음을 번역하세요"),
    HumanMessage(content="안녕하세요!"),
]

model.invoke(messages)
```

아래 모듈은 `langchain_core.output_parsers`에서 `StrOutputParser` 클래스를 가져와서 인스턴스화합니다. `StrOutputParser`는 문자열 출력을 파싱하는 데 사용되며, 이 인스턴스는 다양한 출력 형식을 처리할 때 활용될 수 있습니다.



```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
```

아래 함수는 두 가지 주요 작업을 수행합니다. 첫 번째로, `model.invoke(messages)`를 통해 주어진 메시지를 모델에 전달하고 처리 결과를 받습니다. 그 다음, `parser.invoke(result)`를 사용하여 모델의 처리 결과를 파싱합니다. 이 과정을 통해 데이터를 모델에 적용하고 그 결과를 분석하는 일련의 작업을 간결하게 수행합니다.



```python
result = model.invoke(messages) 
parser.invoke(result) 
```

아래 코드는 객체 `model`과 `parser`를 비트 OR 연산자(`|`)를 사용하여 연결한 후, `chain` 객체를 통해 `messages`를 처리합니다. `chain.invoke(messages)`는 연결된 객체들을 통해 메시지를 처리하는 메서드 호출을 나타냅니다. 이러한 방식은 파이프라인 패턴을 구현할 때 유용하며, 여러 처리 단계를 순차적으로 연결하여 데이터를 처리하는 데 사용됩니다.



```python
chain = model | parser
chain.invoke(messages)
```

`langchain_core.prompts`에서 `ChatPromptTemplate`를 임포트하여 사용합니다. 아래 코드는 사용자로부터 입력받은 텍스트를 특정 언어로 번역하도록 요청하는 시스템 메시지를 생성합니다. `system_template` 변수는 번역 요청 메시지를 정의하며, `prompt_template`는 시스템과 사용자 메시지를 포함하는 `ChatPromptTemplate` 객체를 생성합니다. 이 객체는 대화형 프롬프트에서 사용될 수 있습니다.



```python
from langchain_core.prompts import ChatPromptTemplate

system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)
```

아래 함수는 `prompt_template` 객체의 `invoke` 메서드를 사용하여 특정 텍스트를 처리합니다. 여기서는 `language` 매개변수에 'korean'을, `text` 매개변수에 'hi'를 전달하여 한국어로 된 인사말을 처리하고, 그 결과를 반환합니다.



```python
result = prompt_template.invoke({"language": "korean", "text": "hi"})

result
```

함수 `to_messages()`는 `result` 객체의 데이터를 메시지 형태로 변환하는 역할을 수행합니다. 이 함수는 특정 객체의 상태나 데이터를 사용자에게 전달하기 위한 메시지 형식으로 쉽게 변환할 수 있게 해줍니다.



```python
result.to_messages()
```

### [LCEL(LangChain Expression Language)](https://python.langchain.com/v0.2/docs/concepts/#langchain-expression-language-lcel)



LCEL을 사용하여 LangChain의 기본적인 컴포넌트들을 chaining 기법을 써서 다단계 작업들의 연결 체인을 만들어 복잡한 기능을 구현할 수 있도록 해준다.



```

chain = prompt | model | output_parser

```



`|` 기호는 서로 다른 구성 요소를 연결하고 한 구성 요소의 출력을 다음 구성 요소의 입력으로 전달한다.



이 체인에서 사용자 입력은 프롬프트 템플릿으로 전달되고, 그런 다음 프롬프트 템플릿 출력은 모델로 전달된다. 마지막으로 모델의 결과를 Parser에 전달하여 출력한다.


변수 `chain`은 `prompt_template`, `model`, `parser` 세 부분으로 구성된 파이프라인을 생성합니다. 이 파이프라인은 `invoke` 메소드를 사용하여 입력 데이터를 처리합니다. 여기서, `invoke` 메소드는 `language`와 `text`라는 두 개의 키를 가진 딕셔너리를 인자로 받습니다. 이 예제에서는 `language`에 "korean"을, `text`에 "hi"를 전달하여 파이프라인을 실행합니다.



```python
chain = prompt_template | model | parser
chain.invoke({"language": "korean", "text": "hi"})
```

아래 코드는 FastAPI를 사용하여 간단한 API 서버를 구축하고, LangChain의 Runnable 인터페이스를 활용하여 사용자의 요청을 처리하는 방법을 보여줍니다. 사용자로부터 입력받은 텍스트를 특정 언어로 번역하는 요청을 처리하기 위해, `ChatPromptTemplate`, `ChatOpenAI`, `StrOutputParser`를 순차적으로 연결하는 체인을 생성합니다. 이 체인은 FastAPI 애플리케이션에 라우트로 추가되어, `/chain` 경로로 들어오는 요청을 처리할 수 있게 합니다. 마지막으로, `uvicorn`을 사용하여 로컬 호스트에서 서버를 실행합니다.



```python
# serve.py

from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

# 1. 프롬프트 템플릿 생성
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# 2. 모델 생성
model = ChatOpenAI()

# 3. 파서 생성
parser = StrOutputParser()

# 4. 체인 생성
chain = prompt_template | model | parser


# 4. 앱 정의
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 5. 체인 라우트 추가

add_routes(
    app,
    chain,
    path="/chain",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
```

모든 LangServe 서비스에는 스트리밍 출력과 중간 단계에 대한 가시성을 갖춘 애플리케이션을 구성하고 호출하기 위한 간단한 내장 UI가 제공됩니다.



http://localhost:8000/chain/playground/ 로 이동하여 시도해보세요!


아래 코드는 `langserve` 모듈의 `RemoteRunnable` 클래스를 사용하여 원격 서버에 데이터를 전송하고 실행하는 예제입니다. `RemoteRunnable` 인스턴스를 생성할 때, 원격 서버의 URL을 인자로 제공합니다. 이후 `invoke` 메서드를 사용하여 서버에 `language`와 `text` 키를 포함하는 딕셔너리를 전송합니다. 이 예제에서는 'korean' 언어로, 'hi' 텍스트를 원격 서버에 전송하고 있습니다.



```python
from langserve import RemoteRunnable

# RemoteRunnable 클래스를 langserve 모듈에서 가져옵니다.
remote_chain = RemoteRunnable("http://localhost:8000/chain/")
# 원격 서버에 'korean' 언어로 'hi' 텍스트를 전송하여 실행합니다.
remote_chain.invoke({"language": "korean", "text": "hi"})
```
