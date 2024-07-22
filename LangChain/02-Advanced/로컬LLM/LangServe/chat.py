from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOllama(model="EEVE-Korean-10.8B:latest")

# Prompt 설정
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI Assistant. Your name is 'Anthony'. You must answer in Korean.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm | StrOutputParser()
