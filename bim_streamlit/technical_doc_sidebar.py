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
index_name = st.secrets['PINECONE_INDEX'] if 'PINECONE_INDEX' in st.secrets else  'quantities-qa-openai'
index = pc.Index(index_name)
xq = embeddings.embed_query("all")
res = index.query(vector=xq, top_k=300,include_metadata=True)
section_name_set=set()
sub_section_name_set=set()
task_name_set=set()
for i in (res['matches']):
    section_name_set.add(i['metadata']['section_name'])
    sub_section_name_set.add(i['metadata']['sub_section_name'])
    task_name_set.add(i['metadata']['task_name'])

def technical_doc_sidebar():
    with st.sidebar: 
    # Streamlit app layout
        st.title("Building Information Modeling")
        section_name=st.sidebar.selectbox("Section", ['All']+list(sorted(section_name_set)))
        sub_section_name=st.sidebar.selectbox("Sub Section", ['All']+list(sorted(sub_section_name_set)))
        task_name=st.sidebar.selectbox("Task", ['All']+list(sorted(task_name_set)))
        st.session_state["SECTION"]=section_name
        st.session_state["SUB_SECTION"]=sub_section_name
        st.session_state["TASK"]=task_name
        # Example query to fetch data
        with st.sidebar:
            st.session_state["K_TOP"]= st.radio(
                "K top:",
                ("3","5","10", "20","50", "100", "200"), index=2,horizontal=True
            )
        st.session_state["MIN_COST"]= st.number_input("cost greater than: ", min_value=0, step=10000)
        # Optionally visualize graph data using third-party libraries

        sample_questions = ["what is the total price?", "what is the documenst about?", "what construction items are mentioned in the document?" , 
                            "מה מחיר החפירות?", "מהו הרכיב היקר ביותר?", "באילו חומרים משתמשים?" , "היכן ממוקמים מדפי האש?", "מהן עבודות החשמל המוזכרות?","מהן עבודות האיטום המוזכרות?"]

        AddSampleQuestions(sample_questions)



  