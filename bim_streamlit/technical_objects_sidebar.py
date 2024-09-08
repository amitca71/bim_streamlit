#from constants import SCHEMA_IMG_PATH, LANGCHAIN_IMG_PATH
import streamlit as st
import streamlit.components.v1 as components
from langchain_community.graphs import Neo4jGraph
import json
import networkx as nx
from pyvis.network import Network
from common_functions import AddSampleQuestions
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

pinecone_api_key = st.secrets['PINECONE_API_KEY']
pc = Pinecone(api_key=pinecone_api_key)
index_name = st.secrets['BIM_PINECONE_INDEX'] if 'BIM_PINECONE_INDEX' in st.secrets else  'bim-objects-openai'
index = pc.Index(index_name)
xq = embeddings.embed_query("all")
res = index.query(vector=xq, top_k=500,include_metadata=True)
storey_name_set=set()
object_type_set=set()

for i in (res['matches']):
    storey_name_set.add(i['metadata']['storeyName'])
    object_type_set.add(i['metadata']['objectName'])

def technical_objects_sidebar():
    with st.sidebar: 
    # Streamlit app layout
        st.title("BIM objects search")
        storey_name=st.sidebar.selectbox("floor name", ['All']+list(sorted(storey_name_set)))
        object_type=st.sidebar.selectbox("object type", ['All']+list(sorted(object_type_set)))
        st.session_state["STOREY_NAME"]=storey_name
        st.session_state["OBJECT_TYPE"]=object_type

        # Example query to fetch data
        with st.sidebar:
            st.session_state["K_TOP"]= st.radio(
                "K top:",
                ("3","5","10", "20","50", "100", "200"), index=2,horizontal=True
            )
        # Optionally visualize graph data using third-party libraries

        sample_questions = ["רצפה 25 ס״מ b40", "בטון", "brick" ]

        AddSampleQuestions(sample_questions)



  