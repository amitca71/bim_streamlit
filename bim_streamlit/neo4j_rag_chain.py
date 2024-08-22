from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import ConfigurableField, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from retry import retry
import streamlit as st
from common_functions import ChainClass
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
import streamlit as st
from langchain.chains import RetrievalQA
import logging

from neo4j_rag_retrievers import (
    hypothetic_question_vectorstore,
    parent_vectorstore,
    summary_vectorstore,
    typical_rag,
)
from langchain.callbacks.base import BaseCallbackHandler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

retriever = typical_rag.as_retriever().configurable_alternatives(
    ConfigurableField(id="strategy"),
    default_key="typical_rag",
    parent_strategy=parent_vectorstore.as_retriever(),
    hypothetical_questions=hypothetic_question_vectorstore.as_retriever(),
    summary_strategy=summary_vectorstore.as_retriever(),
)

# Add typing for input
class Question(BaseModel):
    question: str
class RagChainClass(ChainClass):
    def set_chain(self):
        print("setting new graphchain")
        print(self.model_name, self.api_base, self.api_key)
        self.graph_chain=None
        if "gemini" in self.model_name:
            self.rag_llm = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=self.api_key,temperature=0, verbose=True,top_k=200)
        else:
            self.rag_llm = ChatOpenAI(model=self.model_name, openai_api_key=self.api_key,openai_api_base=self.api_base,temperature=0)
        self.vectorstore=Neo4jVector.from_existing_index(
        OpenAIEmbeddings(), index_name="typical_rag", url=st.secrets["DOC_NEO4J_URI"],
        username=st.secrets["DOC_NEO4J_USERNAME"],
        password=st.secrets["DOC_NEO4J_PASSWORD"])
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.rag_llm, chain_type="stuff"
            , retriever=self.vectorstore.as_retriever()
        )      
        
    @retry(tries=1, delay=12)
    def get_results(self, question) -> str:
        """Generate response using Neo4jVector using vector index only

        Args:
            question (str): User query

        Returns:
            str: Formatted string answer with citations, if available.
        """
        logging.info(f"Question: {question}")
        chain_result = self.rag_chain.invoke(question, return_only_outputs=True)
        logging.debug(f"chain_result: {chain_result}")
        result = chain_result["result"]
        return(result)




