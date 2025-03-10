from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import streamlit as st
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import DirectoryLoader

OPENAI_KEY = "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"

# CSV파일 불러오기
from langchain.document_loaders import DirectoryLoader


loader = DirectoryLoader("./hy", glob="*.csv", loader_cls=CSVLoader)
data = loader.load()


# OpenAI Embedding 모델을 이용해서 Chunk를 Embedding 한후 Vector Store에 저장
vectorstore = Chroma.from_documents(
    documents=data, embedding=OpenAIEmbeddings(openai_api_key=OPENAI_KEY)
)
retriever = vectorstore.as_retriever()

# 템플릿 객체 생성
template = """
당신은 한영대학교의 정보에 대해서 알려주는 조수입니다.

다음과 같은 맥락을 사용하여 마지막 질문에 대답하십시오.
모르는 내용에 대해서는 대답하지 마십시오.
답변은 최대 세 문장으로 하고 가능한 한 간결하게 유지하십시오.
교수 또는 학교 정보에 대해 물어봤을때만 관련 내용에 대하여 답하십시오.
학교 이외의 내용을 물어봤을 때는 학교 내용을 배제하고 답하십시오.

말끝마다 상황에 적합한 이모지를 사용하십시오.
{context}
질문: {question}
도움이 되는 답변:"""
rag_prompt_custom = PromptTemplate.from_template(template)

# GPT-3.5 trurbo를 이용해서 LLM 설정
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_KEY)

# RAG chain 설정
from langchain.schema.runnable import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} | rag_prompt_custom | llm
)

# print(rag_chain.invoke(''))

st.title("한영대GPT")
content = st.text_input("한영대에 관련된 질문을 입력하세요!")
if st.button("요청하기"):
    with st.spinner("답변 생성 중..."):
        result = rag_chain.invoke(content)
        st.write(result.content)
