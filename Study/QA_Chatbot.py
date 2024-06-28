import os
import urllib.request
import uuid

import chromadb
import streamlit as st
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from streamlit_pdf_viewer import pdf_viewer

from retriever.multi_retriever import MultiRetriever
from utils import print_messages, create_source_boxes, init_css

load_dotenv()

st.set_page_config(layout="wide", page_title="DaconInfinityGPT", page_icon="🔗", initial_sidebar_state='collapsed')
st.title("Dflex GPT")

# css load
init_css()

# 초기 세션 상태 설정
if "chat_history" not in st.session_state:
  st.session_state.chat_history = []
if "default_pdf" not in st.session_state:
  st.session_state.default_pdf = "./pdf_store/dpdf.pdf"
if "messages" not in st.session_state:
  st.session_state['messages'] = []
if "current" not in st.session_state:
  st.session_state['current'] = {}


@st.cache_resource
def get_embedding():
  model = "solar-embedding-1-large"
  return UpstageEmbeddings(api_key=os.getenv('UPSTAGE_API_KEY'), model=model)


@st.cache_resource
def get_client():
  # ChromaDB 연결
  return chromadb.HttpClient(host=os.getenv('RND_SERVER'), port=8780, settings=Settings(allow_reset=True))


def get_vector_store(select_collection_name="dacon11"):
  return Chroma(client=get_client(), collection_name=select_collection_name, embedding_function=get_embedding())


def get_source_dict():
  return {
    "DSET_AI_01": "지식재산권", "DSET_AI_02": "표준화", "DSET_AI_03": "의료데이터",
    "DSET_AI_05": "데이터기반행정", "DSET_AI_06": "관리지침", "DSET_AI_07": "데이터 3법 개정안",
    "DSET_AI_08": "자치법규", "DSET_AI_09": "ICT", "DSET_AI_10": "빅데이터",
  }

# Function to reset checkbox states
def reset_checkboxes():
  st.session_state.checkbox_states = {f"{col}_check": True for col in get_source_dict().keys()}

# Initialize checkbox states in session state
if 'checkbox_states' not in st.session_state:
  reset_checkboxes()


def get_selected_collections():
  selected_collection = [source for source in get_source_dict().keys() if st.session_state['checkbox_states'][f"{source}_check"]]
  return selected_collection if selected_collection else ["dacon11"]


def get_vector_stores():
  return [get_vector_store(collection) for collection in get_selected_collections()]


def get_multi_retriever():
  return MultiRetriever(vector_stores=get_vector_stores())


@st.cache_resource
def get_prompt():
  system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
  )
  return ChatPromptTemplate.from_messages(
    [
      ('system', system_prompt),
      ('human', '{input}'),
    ]
  )


@st.cache_resource
def get_model():
  return ChatUpstage(api_key=os.getenv('UPSTAGE_API_KEY'))
  # return ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')


@st.cache_resource
def get_chain():
  qa_chain = create_stuff_documents_chain(get_model(), get_prompt())
  return create_retrieval_chain(get_multi_retriever(), qa_chain)


def update_pdf(page_number, code, source):
  print(f"update_pdf 함수 호출, path : {code}, page_number : {page_number}, source: {source}")
  st.session_state['current']['page'] = page_number
  st.session_state['current']['source'] = source
  st.session_state['current']['code'] = code


chat_column, pdf_column = st.columns([5, 3])
chain = get_chain()

with st.sidebar:
  st.title("DB 카테고리 선택")
  for (key, name) in get_source_dict().items():
    st.checkbox(name, value=st.session_state.checkbox_states[f"{key}_check"], key=f"{key}_check")

with chat_column:
  message_container = st.container(height=770)
  print_messages(message_container, show_pdf=update_pdf)

  with st.container():
    if prompt := st.chat_input("메시지를 입력해 주세요.", args=(None,)):
      message_container.chat_message("user").write(f"{prompt}")
      st.session_state["messages"].append({"message": {"role": "user", "content": prompt}})

      response = chain.invoke({'input': prompt})
      answer = response['answer']
      metadata = response['context'][0].metadata

      st.session_state['current']['page'] = metadata["page"]
      st.session_state['current']['source'] = metadata["source"]
      st.session_state['current']['code'] = metadata["data_code"]

      message_container.chat_message("assistant").write(answer)
      if 'context' in response:
        create_source_boxes(message_container, response['context'], update_pdf)

      st.session_state["messages"].append({
        "message": {
          "role": "assistant", "content": answer
        },
        "context": response['context']
      })

with pdf_column:
  with st.container(border=True) as pdf_name_container:
    with st.container():
      pdf_img_col, pdf_content_col = st.columns([1, 3])
      with pdf_img_col:
        st.image("free-icon-pdf.png", width=40, clamp=False)
      with pdf_content_col:
        st.markdown(
          f"""
            <div style="
                white-space: nowrap;
                 overflow: hidden;
                 text-overflow: ellipsis;
                max-width: 100%;
                    ">
              {st.session_state['current']['source'] if 'source' in st.session_state['current'] else ''}
            </div>
          """,
          unsafe_allow_html=True)

    pdf_main_container = st.empty()
    with pdf_main_container:
      # rnd 서버 연결
      if 'code' in st.session_state['current'] and st.session_state['current']['code'] != "":
        pdf_url = f"http://{os.getenv('RND_SERVER')}/dflex/{st.session_state['current']['code']}"
        with urllib.request.urlopen(pdf_url) as pdf_file:
          pdf_viewer(pdf_file.read(), pages_to_render=[st.session_state['current']['page']], height=730, width=700,
                     key=str(uuid.uuid1()))
      else:
        pdf_viewer(st.session_state.default_pdf, height=730, width=700)