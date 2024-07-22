from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="EEVE-Korean-10.8B:latest")

prompt = ChatPromptTemplate.from_template(
    "Translate following sentences into Korean:\n{input}"
)

chain = prompt | llm | StrOutputParser()
