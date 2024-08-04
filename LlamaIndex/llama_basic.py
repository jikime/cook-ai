from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from dotenv import load_dotenv

load_dotenv()


def load_documents(directory):
    """지정된 디렉토리에서 문서를 로드합니다."""
    return SimpleDirectoryReader(directory).load_data()


def create_index(documents):
    """문서로부터 인덱스를 생성합니다."""
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    return VectorStoreIndex.from_documents(documents)


def query_index(index, query):
    """인덱스에 쿼리를 수행하고 응답을 반환합니다."""
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response


def main():
    # 문서 로드
    documents = load_documents("../Assets/data/excel")

    # 인덱스 생성
    index = create_index(documents)

    # 사용자 쿼리 처리
    while True:
        user_query = input("질문을 입력하세요 (종료하려면 'q' 입력): ")
        if user_query.lower() == "q":
            break

        response = query_index(index, user_query)
        print(f"응답: {response}")


if __name__ == "__main__":
    main()
