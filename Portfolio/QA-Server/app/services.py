from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

# LLM 모델 초기화
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, max_tokens=4096)

# 프롬프트 템플릿 정의
prompt_template = """질문에 주어진 문맥을 이용하여 답변을 해주세요. 
답을 모른다면, 답을 만들려고하지 말고 단지 "모른다"라고 말해주세요.

[Context]
{context}

Question: {question}
Answer:"""

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
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
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=OpenAIEmbeddings())
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

    return {"summary": result}
