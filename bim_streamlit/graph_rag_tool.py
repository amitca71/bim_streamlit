from langchain.tools import tool
from neo4j_rag_chain import RagChainClass

class GraphRagTool:
    def __init__(self):
        self.cypher_chain = RagChainClass()

    def update_llm_key(self):
        self.cypher_chain.update_key()

#    @tool("graph-cypher-tool") - AMIT when working with agent this would need to be changed!!
    def run(self, tool_input:str) -> str:
        """
        Useful when answer requires calculating numerical answers like aggregations.
        Use when question asks for a count or how many.
        Use full question as input.
        Do not call this tool more than once.
        Do not call another tool if this returns results.
        """
        print("Tool input is:" + tool_input)
        return (self.cypher_chain.get_results(tool_input))