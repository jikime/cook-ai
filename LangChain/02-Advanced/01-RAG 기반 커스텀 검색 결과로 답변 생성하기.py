from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List
from tqdm.asyncio import tqdm
import asyncio

# LLM 및 임베딩 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

# 문서 로드
folder_path = "../../Assets/data/사업보고서"
loader = DirectoryLoader(folder_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()


# 문서 분할
def split_docs(documents, chunk_size=1024, chunk_overlap=20):
    # 주어진 문서를 분할하기 위한 텍스트 분할기를 생성합니다.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    # 문서를 분할합니다.
    docs = text_splitter.split_documents(documents)
    return docs


# 문서를 분할합니다.
docs = split_docs(documents)

# 벡터 저장소 생성
vectorstore = Chroma.from_documents(docs, embed_model)

# 쿼리 재작성 프롬프트
query_prompt = PromptTemplate(
    input_variables=["count", "query"],
    template="""
너는 주어진 질문에 대한 정보를 찾을 수 있도록 여러개의 질문를 생성하는 인공지능이야.
주어진 질문를 참고하여서 주어진 질문에 대한 정보를 찾을 수 있는 {count} 개의 새로운 질문를 만들어줘.
한 줄에 하나의 질문만 작성 해줘. 번호나 다른 인덱싱은 하지 말아줘.
질문: {query}
새로운 쿼리:
""",
)

# 벡터 검색기 및 BM25 검색기 설정
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3


def generate_queries(query: str, count: int = 5) -> List[str]:
    prompt = query_prompt.format(count=count - 1, query=query)
    # LLM을 사용하여 응답 생성
    response = llm.invoke(prompt)

    # 응답을 줄 단위로 분할
    generated_queries = response.content.split("\n")
    cleaned_queries = [query.strip() for query in generated_queries]

    # 원본 쿼리를 리스트의 첫 번째 항목으로 추가
    all_queries = [query] + cleaned_queries

    # 생성된 쿼리 수가 요청된 수보다 많은 경우 잘라내기
    return all_queries[:count]


def merge_results_by_sim_score(
    results: List[List[Document]], similarity_top_k: int = 5
) -> List[Document]:
    merge_scores = {}
    for docs in results:
        for doc in docs:
            if doc.page_content not in merge_scores:
                merge_scores[doc.page_content] = doc.metadata.get("score", 0.0)
            else:
                merge_scores[doc.page_content] = max(
                    merge_scores[doc.page_content], doc.metadata.get("score", 0.0)
                )

    reranked_results = sorted(merge_scores.items(), key=lambda x: x[1], reverse=True)
    return [
        Document(page_content=content, metadata={"score": score})
        for content, score in reranked_results[:similarity_top_k]
    ]


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


async def get_related_docs(
    query_string: str, num_generate_query: int = 3, similarity_top_k: int = 3
) -> str:
    queries = generate_queries(query_string, num_generate_query)
    task_results = await run_queries(queries, [vector_retriever, bm25_retriever])
    final_results = merge_results_by_sim_score(task_results, similarity_top_k)

    related_docs = ""
    for i, doc in enumerate(final_results):
        related_docs += f"\n[{i}]: {doc.page_content}\n"
    return related_docs


async def answer(query):
    # 주어진 질문에 대한 관련 문서를 비동기적으로 검색합니다.
    docs = await get_related_docs(
        query_string=query, num_generate_query=3, similarity_top_k=10
    )
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


# 사용 예시
async def main():
    query_list = [
        "현재 삼성전자의 최대 주주는 누구인가요?",
        "삼성전자의 DX부문 매출액은 얼마인가요?",
    ]

    for q in query_list:
        print(f"Q: {q}")
        print(f"A: {await answer(q)}")
        print("\n=========================\n")


if __name__ == "__main__":
    asyncio.run(main())
