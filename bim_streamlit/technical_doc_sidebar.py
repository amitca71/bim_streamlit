#from constants import SCHEMA_IMG_PATH, LANGCHAIN_IMG_PATH
import streamlit as st
import streamlit.components.v1 as components
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase
import json
import networkx as nx
from pyvis.network import Network
from common_functions import AddSampleQuestions

url = st.secrets["DOC_NEO4J_URI"]
username = st.secrets["DOC_NEO4J_USERNAME"]
password = st.secrets["DOC_NEO4J_PASSWORD"]

neo4j_conn = GraphDatabase.driver(
    uri=url, auth=(username, password)
 )
def fetch_data(query):
    with neo4j_conn.session() as session:
        result = session.run(query)
        return [record for record in result]



# Streamlit app layout
st.title("Building Information Modeling")

# Example query to fetch data

# Optionally visualize graph data using third-party libraries
import networkx as nx
# Get all secrets

rag_strategy_list=["typical_rag","parent_document", "hypothetical_questions"]
def technical_doc_sidebar():
    with st.sidebar: 
#        st.title("Neo4j Graph Visualization with Relationships")
        # Streamlit app
        rag_strategy=st.sidebar.selectbox("Select RAG strategy", rag_strategy_list)
        n="Parent"
        r="HAS_CHILD"
        m="Child"
        if (rag_strategy=="hypothetical_questions"):
            r="HAS_QUESTION"
            m="Question"
        st.session_state["RAG_STRATEGY"]=rag_strategy
        st.title('Graph Visualization')
        G = nx.Graph()

        # Example query to fetch data
        query = f"""
        MATCH (n:{n})-[r:{r}]->(m:{m}) RETURN n, r, m LIMIT 5;
        """
        results = fetch_data(query)
            
        for record in results:
            node1 = record["n"]
            node2 = record["m"]
            relationship = record["r"]
            G.add_node(node1["id"], label=list(node1.labels)[0], properties=dict(node1))
            G.add_node(node2["id"], label=list(node2.labels)[0], properties=dict(node2))
            G.add_edge(node1["id"], node2["id"], label=relationship.type, properties=dict(relationship))
        net = Network(notebook=False, height="500px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote')
 
        net.from_nx(G)
        html_content = net.generate_html(notebook=False)
        st.components.v1.html(html_content, height=400) 
        sample_questions = ["what is the appartment number", "באיזה קומה הדירה?", "מה אורך ארונות המטבח?", 
                            "באיזה רחוב הבניין?", "מה יש בקומת המרתף" , "האם יש ממד בדירה?", "אילו דלתות יש בחדרי המדרגות?"]

        AddSampleQuestions(sample_questions)


  