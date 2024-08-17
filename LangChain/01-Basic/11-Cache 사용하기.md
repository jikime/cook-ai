**주요내용**
- 🤖 `langchain_openai` 라이브러리를 사용해 AI 챗봇 생성
- 🌐 요약을 위한 `PromptTemplate` 사용
- ⏱️ 코드 실행 시간 측정하기
- 💾 `InMemoryCache`와 `SQLiteCache`로 캐싱 전략 구현


```python
# .env 파일에서 환경 변수를 로드합니다.
from dotenv import load_dotenv

load_dotenv()
```

이 코드는 `langchain_openai` 라이브러리에서 `ChatOpenAI` 클래스를 임포트하고, `gpt-4o-mini` 모델을 사용하여 챗봇 인스턴스를 생성합니다. `ChatOpenAI` 클래스는 OpenAI의 언어 모델을 활용하여 대화형 AI를 구현할 수 있게 해주며, 여기서는 `gpt-4o-mini` 모델을 사용하여 인스턴스를 초기화합니다.



```python
from langchain_openai import ChatOpenAI

# gpt-4o-mini 모델을 사용하여 ChatOpenAI 객체를 생성합니다.
llm = ChatOpenAI(model_name="gpt-4o-mini")
```

이 코드는 `langchain.prompts`에서 `PromptTemplate` 클래스를 임포트하고, `{country} 에 대해서 요약해줘`라는 템플릿 문자열을 사용하여 `PromptTemplate` 객체를 생성합니다. 생성된 객체는 특정 국가에 대한 요약을 요청하는 프롬프트로 사용될 수 있습니다.



```python
from langchain.prompts import PromptTemplate

# {country} 에 대해서 요약해줘라는 템플릿을 사용하여 PromptTemplate 객체를 생성합니다.
prompt = PromptTemplate.from_template("{country} 에 대해서 요약해줘")
prompt
```

이 함수는 `chain` 객체의 `invoke` 메서드를 사용하여 "한국"에 대한 정보를 요청하고, 결과를 출력합니다. `%%time` 매직 커맨드를 사용하여 코드 블록의 실행 시간을 측정합니다. 이는 주로 성능 측정이나 디버깅 시 유용하게 사용됩니다.



```python
# %%time 
# 실행 시간을 측정합니다.
response = chain.invoke({"country": "한국"})
# 응답 내용을 출력합니다.
print(response.content)
```

### InMemoryCache


이 함수는 `langchain` 라이브러리의 글로벌 설정을 변경하여, 언어 모델의 캐시 시스템을 `InMemoryCache`로 설정합니다. `set_llm_cache` 함수는 캐시 시스템을 설정하는 데 사용되며, `InMemoryCache` 클래스의 인스턴스를 생성하여 이를 인자로 전달합니다. 이를 통해 언어 모델의 결과를 메모리 내에서 캐싱할 수 있게 됩니다.



```python
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# InMemoryCache() 인스턴스를 생성하여 set_llm_cache 함수에 전달합니다.
set_llm_cache(InMemoryCache())
```

이 코드는 `chain` 객체의 `invoke` 메서드를 사용하여 "한국"에 대한 응답을 요청하고, 받아온 응답의 내용(`content`)을 출력합니다. `%%time` 매직 커맨드를 사용하여 코드 블록의 실행 시간을 측정합니다.



```python
# %%time
# 응답을 받아와 출력합니다. 여기서는 "한국"이라는 국가를 매개변수로 사용합니다.
response = chain.invoke({"country": "한국"})
print(response.content)
```

### SQLite Cache


이 함수는 `langchain` 라이브러리의 글로벌 설정을 사용하여 LLM(Language Learning Model) 캐시를 SQLite 데이터베이스로 설정합니다. `set_llm_cache` 함수는 `SQLiteCache` 인스턴스를 인자로 받으며, 이 인스턴스는 `database_path` 매개변수를 통해 데이터베이스 파일의 위치를 지정합니다. 이를 통해 LLM 모델의 캐시 데이터를 관리하는 방법을 제공합니다.



```python
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

# LLM 캐시를 SQLite 데이터베이스로 설정합니다.
set_llm_cache(SQLiteCache(database_path="llm_cache.db"))
```

이 함수는 `chain` 객체의 `invoke` 메서드를 사용하여 특정 국가에 대한 정보를 요청하고, 그 응답을 출력합니다. 여기서는 `"한국"`이라는 국가를 인자로 전달합니다. 또한, 실행 시간을 측정하기 위해 매직 커맨드 `%%time`을 사용합니다.



```python
# %%time
# 실행 시간을 측정합니다.
response = chain.invoke({"country": "한국"})
# 응답을 출력합니다.
print(response)
```
