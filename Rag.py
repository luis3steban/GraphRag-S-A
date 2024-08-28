from dotenv import load_dotenv
import os

from langchain_community.graphs import Neo4jGraph

# Warning control
import warnings
warnings.filterwarnings("ignore")
load_dotenv('.env', override=True)
NEO4J_URI = os.getenv('bolt://localhost:7687')
NEO4J_USERNAME = os.getenv('neo4j')
NEO4J_PASSWORD = os.getenv('pwd4admin')
NEO4J_DATABASE = os.getenv('neo4j')

kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
) 

cypher = """
  MATCH (n) 
  RETURN count(n) AS numberOfNodes
  """
result = kg.query(cypher)
result
print(f"There are {result[0]['numberOfNodes']} nodes in this graph.")