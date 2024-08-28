from neo4j import GraphDatabase
import os
from neo4j_genai.retrievers import VectorRetriever
from neo4j_genai.embeddings.openai import OpenAIEmbeddings
from neo4j import GraphDatabase
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "pwd4admin")
driver = GraphDatabase.driver(URI, auth=AUTH)
embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
retriever = VectorRetriever(
    driver,
    index_name="region_text_embeddings",
    embedder=embedder,
    return_properties=["STOCK_AGOTADO"],
)
os.environ["OPENAI_API_KEY"] = ""
# Demo database credentials
URI = "neo4j+s://demo.neo4jlabs.com"
AUTH = ("recommendations", "recommendations")