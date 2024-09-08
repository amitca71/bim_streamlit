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
from langchain_community.vectorstores import pinecone as vpc
from langchain_openai import OpenAIEmbeddings
import streamlit as st
from langchain.chains import RetrievalQA
import logging
from langchain.callbacks import get_openai_callback
from langchain.chains.conversation.memory import ConversationBufferMemory

    #from langchain_pinecone import PineconeVectorStore  

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
MEMORY = ConversationBufferMemory(
    memory_key="chat_history", 
    input_key='query', 
    output_key='result', 
    return_messages=True,
    max_token_limit=5000)


# Add typing for input
class Question(BaseModel):
    question: str


from pinecone import Pinecone



class RagChainClass(ChainClass):
    def set_chain(self):
        print("setting new pinecone graph chain")
        print(self.model_name, self.api_base, self.api_key)
        self.graph_chain=None
        if "gemini" in self.model_name:
            self.rag_llm = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=self.api_key,temperature=0, verbose=True)
        else:
            self.rag_llm = ChatOpenAI(model=self.model_name, openai_api_key=self.api_key,openai_api_base=self.api_base,temperature=0)
        pinecone_api_key = st.secrets["PINECONE_API_KEY"]
        index_name = 'bim-objects-openai'
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(index_name)
#        print(self.index.describe_index_stats())

        self.vectorstore = vpc.Pinecone(self.index,embedding=OpenAIEmbeddings(), text_key="text").\
            from_existing_index(index_name=index_name,embedding=OpenAIEmbeddings(),text_key="text")
        top_k=int(st.session_state["K_TOP"]) if "K_TOP" in st.session_state else 15
        filter={}
        if "storeyName" in st.session_state and st.session_state['storeyName'] !='All':
            filter["storeyName"]={'$eq': st.session_state["storeyName"]}
        if "objectType" in st.session_state and st.session_state['objectType'] !='All':
            print("objectType:", st.session_state['objectType'])
            filter["objectType"]={'$eq': st.session_state["objectType"]}
        if "CrossSectionArea" in st.session_state and float(st.session_state['CrossSectionArea']) >0:
            filter["CrossSectionArea"]={'$gt': float(st.session_state["CrossSectionArea"])}
        if "Depth" in st.session_state and float(st.session_state['Depth']) >0:
            filter["Depth"]={'$gt': float(st.session_state["Depth"])}       
        if "GrossArea" in st.session_state and float(st.session_state['GrossArea']) >0:
            filter["GrossArea"]={'$gt': float(st.session_state["GrossArea"])}           
        if "GrossFootprintArea" in st.session_state and float(st.session_state['GrossFootprintArea']) >0:
            filter["GrossFootprintArea"]={'$gt': float(st.session_state["GrossFootprintArea"])}      
        if "GrossSideArea" in st.session_state and float(st.session_state['GrossSideArea']) >0:
            filter["GrossSideArea"]={'$gt': float(st.session_state["GrossSideArea"])}     
        if "GrossVolume" in st.session_state and float(st.session_state['GrossVolume']) >0:
            filter["GrossVolume"]={'$gt': float(st.session_state["GrossVolume"])}   
        if "Height" in st.session_state and float(st.session_state['Height']) >0:
            filter["Height"]={'$gt': float(st.session_state["Height"])}    
        if "Length" in st.session_state and float(st.session_state['Length']) >0:
            filter["Length"]={'$gt': float(st.session_state["Length"])}   
        if "NetArea" in st.session_state and float(st.session_state['NetArea']) >0:
            filter["NetArea"]={'$gt': float(st.session_state["NetArea"])}  
        if "NetSideArea" in st.session_state and float(st.session_state['NetSideArea']) >0:
            filter["NetSideArea"]={'$gt': float(st.session_state["NetSideArea"])}  
        if "NetVolume" in st.session_state and float(st.session_state['NetVolume']) >0:
            filter["NetVolume"]={'$gt': float(st.session_state["NetVolume"])}  
        if "OuterSurfaceArea" in st.session_state and float(st.session_state['OuterSurfaceArea']) >0:
            filter["OuterSurfaceArea"]={'$gt': float(st.session_state["OuterSurfaceArea"])}  
        if "Perimeter" in st.session_state and float(st.session_state['Perimeter']) >0:
            filter["Perimeter"]={'$gt': float(st.session_state["Perimeter"])}  
        if "Width" in st.session_state and float(st.session_state['Width']) >0:
            filter["Width"]={'$gt': float(st.session_state["Width"])}  
        self.rag_chain = RetrievalQA.from_chain_type(  
            llm=self.rag_llm,  
            chain_type="stuff",  
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": top_k, 'filter':filter } ) ,
            memory=MEMORY
        )  

    @retry(tries=1, delay=12)
    def get_results(self, question) -> str:
        """Generate response using Pinecone Vector using vector index only

        Args:
            question (str): User query

        Returns:
            str: Formatted string answer with citations, if available.
        """
        logging.info(f"Question: {question}")
        embedding=OpenAIEmbeddings()
        query_vector = embedding.embed_query(question)

        # Query the retriever directly
        retriever = self.rag_chain.retriever
        results = retriever.get_relevant_documents(question)

        # Print details of each match
#        for match in results:
#            print(match)
        cb=None
#        with get_openai_callback() as cb:
#            embedding=OpenAIEmbeddings()
#            chain_result = self.rag_chain.invoke(question, return_only_outputs=False, verbose=True)
#            print (cb)
#        result = chain_result["result"]
        result=results
        return(result, cb)




