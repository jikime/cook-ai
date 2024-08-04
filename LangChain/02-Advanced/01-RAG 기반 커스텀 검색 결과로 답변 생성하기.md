**주요내용**
- 🛠 `.env` 파일을 사용한 **환경 변수 관리**로 코드 보안 강화
- 📁 **DirectoryLoader**와 **PyPDFLoader**를 통한 다양한 형식의 문서 로드
- 🤖 **langchain_openai** 라이브러리를 활용한 **언어 모델**과 **프롬프트 템플릿**의 사용
- 🔍 **비동기 검색**과 **BM25Retriever**로 효율적인 문서 검색 및 결과 병합
- 💡 **LLM**을 사용하여 관련 쿼리 생성 및 답변 추출

`load_dotenv` 함수를 호출함으로써, `.env` 파일 내에 정의된 환경 변수들이 프로그램의 환경 변수로 로드됩니다. 이는 보안이 중요한 정보(예: 데이터베이스 비밀번호, API 키 등)를 코드에 직접 하드코딩하지 않고 관리할 수 있는 효과적인 방법을 제공합니다.



```python
# .env 파일에서 환경 변수를 로드합니다.
from dotenv import load_dotenv

load_dotenv()
```

<br>``DirectoryLoader``는 주로 텍스트 파일을 로드하는 데 사용되지만, ``glob`` 매개변수와 ``loader_cls`` 매개변수를 통해 다른 형식의 파일도 로드할 수 있습니다. 여기서는 ``PyPDFLoader``를 사용하여 PDF 파일을 로드합니다. 사용자는 ``folder_path`` 변수를 통해 로드할 파일이 위치한 디렉토리 경로를 지정합니다. 이 경우, 사업보고서가 포함된 디렉토리에서 모든 PDF 파일(``**/*.pdf``)을 로드하기 위해 설정되었습니다.



```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

folder_path = './data/사업보고서'
loader = DirectoryLoader(folder_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()
```

<br>아래 코드는 `langchain_openai` 라이브러리에서 `ChatOpenAI`와 `OpenAIEmbeddings` 클래스를 임포트합니다. `ChatOpenAI` 인스턴스는 `gpt-4o-mini` 모델을 사용하며, `temperature`를 0.1로 설정하여 생성됩니다. 이는 생성된 텍스트의 예측 가능성을 높이고, 더 일관된 결과를 얻기 위함입니다. `OpenAIEmbeddings` 인스턴스는 `text-embedding-3-small` 모델을 사용하며, 데이터 처리 시 청크 크기를 256으로 설정하여 생성됩니다. 이는 텍스트 임베딩을 생성하는 데 사용됩니다.



```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
embed_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    chunk_size=256
)
```

<br>아래 함수는 문서를 분할하고, 분할된 문서들을 사용하여 벡터 저장소를 생성합니다. `split_docs` 함수는 `RecursiveCharacterTextSplitter`를 사용하여 주어진 문서를 특정 크기(`chunk_size`)와 겹침(`chunk_overlap`)을 가진 여러 부분으로 분할합니다. 이후, `Chroma.from_documents` 함수는 분할된 문서들과 임베딩 모델을 사용하여 벡터 저장소를 생성합니다. 이 과정은 텍스트 기반 데이터를 처리하고, 이를 벡터 형태로 저장하여 더 효율적인 검색, 분류, 또는 다른 자연어 처리 작업을 가능하게 합니다.



```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

def split_docs(documents, chunk_size=1024, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
    )
    docs = text_splitter.split_documents(documents)
    return docs

docs = split_docs(documents)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embed_model
)
```

<br>아래 코드는 `langchain.prompts`에서 `PromptTemplate` 클래스를 가져와 사용합니다. 사용자가 제공한 질문에 대해 AI가 여러 개의 새로운 질문을 생성할 수 있도록 하는 프롬프트 템플릿을 정의합니다. 이 템플릿은 사용자가 지정한 질문(`query_string`)을 기반으로, 지정된 개수(`count`)만큼 새로운 질문을 생성하는 데 사용됩니다. `PromptTemplate` 클래스의 인스턴스를 생성할 때는 입력 변수로 질문의 개수와 질문 내용을 포함하는 리스트를 전달합니다.



```python
from langchain_core.prompts import PromptTemplate

query_string = "현재 삼성전자의 최대 주주는 누구인가요?"

query_prompt = """
너는 주어진 질문에 대한 정보를 찾을 수 있도록 여러개의 질문를 생성하는 AI야.
주어진 질문를 기반으로 정보를 찾을 수 있는 {count} 개의 새로운 질문를 만들어줘.
한 줄에 하나의 질문만 작성해주고 인덱스 번호는 필요없어.
질문: {query}
새로운 질문:
"""

prompt_template = PromptTemplate(
    input_variables=["count", "query"],
    template=query_prompt
)
```

<br>아래 함수는 주어진 쿼리 문자열과 생성할 쿼리의 수를 인자로 받아, LLM(Large Language Model)을 사용하여 새로운 쿼리들을 생성합니다. 함수는 먼저 주어진 쿼리를 포함하는 프롬프트를 생성하고, 이를 LLM에 전달하여 응답을 받습니다. 응답된 내용은 줄 단위로 분할되어, 각 쿼리가 공백 없이 정리됩니다. 그 후, 원본 쿼리를 생성된 쿼리 리스트의 첫 번째 항목으로 추가합니다. 마지막으로, 요청된 쿼리 수만큼의 쿼리를 반환하기 위해 리스트를 적절히 잘라냅니다. 이 과정을 통해, 사용자는 원하는 수의 관련 쿼리를 얻을 수 있습니다.



```python
from typing import List

def generate_queries(query: str, count: int = 5) -> List[str]:
    # 프롬프트 생성
    prompt = prompt_template.format(
        count=count - 1, 
        query=query
    )
    
    # LLM을 사용하여 응답 생성
    response = llm.invoke(prompt)
    
    # 응답을 줄 단위로 분할
    generated_queries = response.content.split("\n")
    cleaned_queries = [query.strip() for query in generated_queries]
    
    # 원본 쿼리를 리스트의 첫 번째 항목으로 추가
    all_queries = [query] + cleaned_queries
    
    # 생성된 쿼리 수가 요청된 수보다 많은 경우 잘라내기
    return all_queries[:count]
```

<br>함수 `generate_queries`는 주어진 `query_string`을 사용하여 지정된 수의 쿼리를 생성합니다. 여기서는 `query_string`을 기반으로 5개의 쿼리를 생성하고, 이를 출력합니다. 이 함수는 검색 쿼리, 데이터베이스 쿼리 생성 등 다양한 목적으로 활용될 수 있습니다.



```python
# query_string 변수를 사용하여 5개의 쿼리를 생성합니다.
queries = generate_queries(query_string, 5)
# 생성된 쿼리들을 출력합니다.
print(queries)
```

<br>아래 함수는 비동기적으로 여러 검색기(`retrievers`)를 사용하여 다양한 쿼리(`queries`)를 실행합니다. 각 쿼리와 검색기 조합에 대해 별도의 비동기 작업을 생성하고, `asyncio.to_thread`를 사용하여 이러한 작업을 병렬로 실행합니다. 작업의 실행은 `tqdm`을 사용하여 진행 상황을 시각적으로 표시하며, 모든 작업이 완료되면 결과를 수집하여 반환합니다.



```python
from tqdm.asyncio import tqdm
import asyncio

async def run_queries(queries, retrievers):
    # 각 쿼리와 검색기에 대해 비동기 작업을 생성합니다.
    tasks = []
    for query in queries:
        for retriever in retrievers:
            tasks.append(
                asyncio.create_task(asyncio.to_thread(retriever.invoke, query))
            )

    # 모든 작업을 비동기적으로 실행하고 결과를 수집합니다.
    task_results = await tqdm.gather(*tasks)

    return task_results
```

<br>아래 코드는 `langchain.retrievers`에서 `BM25Retriever`를 가져와서 사용합니다. 먼저, `vectorstore`를 사용하여 유사성 기반 검색을 위한 벡터 검색기를 설정합니다. 여기서는 최근접 이웃 검색에 사용될 이웃의 수(`k`)를 3으로 설정합니다. 그 다음, `BM25Retriever`를 사용하여 문서 집합에서 BM25 검색기를 설정합니다. 이 검색기 역시 `k` 값을 3으로 설정하여 상위 3개의 가장 관련성 높은 문서를 검색 결과로 반환하도록 합니다.



```python
from langchain_community.retrievers import BM25Retriever

# 벡터 검색기 설정
vector_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

# BM25 검색기 설정
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3
```

<br>아래 함수는 여러 문서 집합에서 각 문서의 유사도 점수를 기반으로 상위 `k`개의 가장 유사한 문서를 선택하여 병합합니다. `merge_results_by_similarity_score` 함수는 두 매개변수를 받습니다: `results`, 여러 문서 집합의 리스트를 나타내며, 각 문서는 `Document` 객체입니다; `similarity_top_k`, 반환할 상위 문서의 수를 지정합니다(기본값은 5). 각 `Document` 객체의 `page_content`를 키로 하고, `metadata`에서 `score`를 값으로 하는 딕셔너리를 생성하여 유사도 점수를 기반으로 문서를 병합합니다. 이후, 점수가 높은 순으로 문서를 정렬하고 상위 `k`개 문서를 반환합니다.



```python
from langchain_core.documents import Document

def merge_results_by_similarity_score(
    results: List[List[Document]], similarity_top_k: int = 5
) -> List[Document]:
    # 유사도 점수에 따라 결과를 병합하는 함수
    merge_scores = {}
    for docs in results:
        for doc in docs:
            # 문서의 페이지 내용이 merge_scores에 없으면 추가
            if doc.page_content not in merge_scores:
                merge_scores[doc.page_content] = doc.metadata.get("score", 0.0)
            else:
                # 이미 존재하면 최대 점수를 유지
                merge_scores[doc.page_content] = max(
                    merge_scores[doc.page_content], doc.metadata.get("score", 0.0)
                )

    # 점수에 따라 결과를 내림차순으로 정렬
    ranked_results = sorted(merge_scores.items(), key=lambda x: x[1], reverse=True)
    # 상위 k개의 유사한 문서를 반환
    return [
        Document(page_content=content, metadata={"score": score})
        for content, score in ranked_results[:similarity_top_k]
    ]
```

<br>아래 함수는 주어진 쿼리 문자열에 기반하여 관련 문서를 비동기적으로 검색하고, 결과를 문자열로 반환합니다. `generate_queries` 함수를 사용하여 주어진 쿼리 문자열로부터 여러 쿼리를 생성합니다. 이후, `run_queries` 함수를 통해 생성된 쿼리들을 실행하고, `vector_retriever`와 `bm25_retriever` 검색 엔진을 사용하여 결과를 얻습니다. 얻은 결과는 `merge_results_by_similarity_score` 함수를 통해 유사도 점수에 따라 병합되며, 상위 `similarity_top_k`개의 문서만 최종 결과로 선택됩니다. 최종적으로, 선택된 문서들의 내용은 순서대로 문자열에 추가되어 반환됩니다.



```python
async def get_related_docs(
    query_string: str, num_generate_query: int = 3, similarity_top_k: int = 3
) -> str:
    # 주어진 쿼리 문자열로부터 쿼리를 생성합니다.
    queries = generate_queries(query_string, num_generate_query)
    # 생성된 쿼리를 실행하여 결과를 얻습니다.
    task_results = await run_queries(queries, [vector_retriever, bm25_retriever])
    # 유사도 점수에 따라 결과를 병합합니다.
    final_results = merge_results_by_similarity_score(task_results, similarity_top_k)

    # 최종 결과로부터 관련 문서를 문자열로 구성합니다.
    related_docs = ""
    for i, doc in enumerate(final_results):
        related_docs += f"\n[{i}]: {doc.page_content}\n"
    return related_docs
```

<br>아래 함수는 비동기 방식으로 `get_related_docs` 함수를 호출하여 특정 쿼리 문자열에 대한 관련 문서를 검색합니다. 검색된 문서는 `docs` 변수에 저장되며, 이후 `print` 함수를 사용하여 결과를 출력합니다. `query_string` 매개변수를 통해 검색하고자 하는 쿼리를 전달합니다.



```python
# 비동기 함수를 사용하여 관련 문서를 가져옵니다.
docs = await get_related_docs(query_string="삼성전자의 DX부문 매출액은 얼마인가요?")
# 결과를 출력합니다.
print(docs)
```

<br>아래 함수는 사용자의 질문(`query`)을 받아, 관련 문서를 검색하고, 이를 바탕으로 언어 모델에 질문을 제시하여 답변을 얻는 비동기 함수입니다. 먼저, `get_related_docs` 함수를 사용하여 주어진 질문과 관련된 문서를 검색합니다. 이때, 검색할 쿼리의 수(`num_generate_query`)와 유사도가 높은 상위 문서의 수(`similarity_top_k`)를 지정합니다. 검색된 문서는 프롬프트 생성에 사용되며, 이 프롬프트는 언어 모델(`llm`)을 호출하는 데 사용됩니다. 마지막으로, 언어 모델의 응답(`response.content`)을 반환합니다.



```python
async def answer(query):
  # 주어진 질문에 대한 관련 문서를 비동기적으로 검색합니다.
  docs = await get_related_docs(query_string=query, num_generate_query=3, similarity_top_k=10)
  # 사용자의 질문과 관련된 문서를 바탕으로 프롬프트를 생성합니다.
  prompt = f"""
  주어진 문서를 활용하여 사용자의 질문에 대해 친절하게 답변해줘

  문서
  {docs}

  질문: {query}
  """
  # 생성된 프롬프트를 사용하여 언어 모델을 호출합니다.
  response = llm.invoke(prompt)
  # 언어 모델의 응답 내용을 반환합니다.
  return response.content
```

<br>아래 코드는 `query_list`에 저장된 질문 목록을 순회하며 각 질문에 대한 답변을 비동기적으로 요청합니다. 각 질문(`q`)에 대해, 질문을 출력하고 `answer(q)` 함수를 통해 얻은 답변을 출력한 후, 구분선을 출력합니다. `answer` 함수는 비동기 함수로 가정되며, 각 질문에 대한 답변을 반환합니다.



```python
query_list = ["현재 삼성전자의 최대 주주는 누구인가요?", "삼성전자의 DX부문 매출액은 얼마인가요?"]

for q in query_list:
  print(f"Q: {q}")
  print(f"A: {await answer(q)}")
  print("\n=========================\n")
```
