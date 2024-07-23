from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import os

load_dotenv()

# 모델 선택을 위한 환경 변수 (기본값은 'openai')
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# OpenAI 모델 초기화
openai_llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    max_tokens=4096,
)

# Ollama 모델 초기화
ollama_llm = ChatOllama(
    model="qwen2:7b-instruct-q8_0",
)

# 선택된 모델 제공자에 따라 LLM 선택
llm = openai_llm if MODEL_PROVIDER == "openai" else ollama_llm

# 프롬프트 템플릿 정의
# prompt_template = """
# 당신은 메일 비즈니스를 담당해 주는 인공지능 챗봇이에요.
# 메일 내용을 참고하여서 사용자의 질문에 친절하게 답변해주세요.
# 단, 메일 내용에는 서명, 날짜, 장소, 이메일 주소, 전화번호 또는 기타 개인 정보가 포함되어 있을 수 있어요.
# 이러한 정보는 제공하지 말아주세요.
# 그리고 답을 모른다면, 답을 만들려고하지 말고 단지 "모른다"라고 말해주세요.

# [메일 내용]
# {context}

# [질문]
# {question}

# [답변]
# """

# prompt = PromptTemplate(
#     template=prompt_template, input_variables=["context", "question"]
# )

system_prompt = """
당신은 메일 비즈니스를 담당해 주는 인공지능 챗봇이에요.
메일 내용을 참고하여서 사용자의 질문에 친절하게 답변해주세요.
단, 메일 내용에는 서명, 날짜, 장소, 이메일 주소, 전화번호 또는 기타 개인 정보가 포함되어 있을 수 있어요.
이러한 정보는 제공하지 말아주세요. 
그리고 답을 모른다면, 답을 만들려고하지 말고 단지 "모른다"라고 말해주세요.

[메일 내용]
{context}
"""

user_prompt = """
[질문]
{question}

[답변]
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", user_prompt),
    ]
)


# CharacterTextSplitter를 사용하여 텍스트를 청크로 분할
def split_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    docs = text_splitter.split_text(text)
    return docs


def get_vectorstore(text_chunks):
    if MODEL_PROVIDER == "openai":
        embeddings = OpenAIEmbeddings()
    else:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def build_chain(retriever, llm):
    # 체인을 구성
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


async def analyze_text(context: str, question: str):
    # 텍스트 분할
    texts = split_text(context)

    # 임베딩 및 벡터 저장소 생성
    vectorstore = get_vectorstore(texts)

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    )

    chain = build_chain(retriever, llm)
    result = chain.invoke(question)

    return {"contents": result}
