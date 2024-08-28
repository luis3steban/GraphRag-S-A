import os
from dotenv import load_dotenv
load_dotenv('.env', override=True)
from graphdatascience import GraphDataScience
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='neo4j')

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_AUTH = None
if os.environ.get("NEO4J_USERNAME") and os.environ.get("NEO4J_PASSWORD"):
    NEO4J_AUTH = (
        os.environ.get("NEO4J_USERNAME"),
        os.environ.get("NEO4J_PASSWORD"),
    )

gds = GraphDataScience(NEO4J_URI, auth=NEO4J_AUTH)

from graphdatascience.server_version.server_version import ServerVersion

assert gds.server_version() >= ServerVersion(1, 8, 0)

_ = gds.run_cypher(
    """
        CREATE
         (dan:Person {name: 'Dan'}),
         (annie:Person {name: 'Annie'}),
         (matt:Person {name: 'Matt'}),
         (jeff:Person {name: 'Jeff'}),
         (brie:Person {name: 'Brie'}),
         (elsa:Person {name: 'Elsa'}),

         (cookies:Product {name: 'Cookies'}),
         (tomatoes:Product {name: 'Tomatoes'}),
         (cucumber:Product {name: 'Cucumber'}),
         (celery:Product {name: 'Celery'}),
         (kale:Product {name: 'Kale'}),
         (milk:Product {name: 'Milk'}),
         (chocolate:Product {name: 'Chocolate'}),

         (dan)-[:BUYS {amount: 1.2}]->(cookies),
         (dan)-[:BUYS {amount: 3.2}]->(milk),
         (dan)-[:BUYS {amount: 2.2}]->(chocolate),

         (annie)-[:BUYS {amount: 1.2}]->(cucumber),
         (annie)-[:BUYS {amount: 3.2}]->(milk),
         (annie)-[:BUYS {amount: 3.2}]->(tomatoes),

         (matt)-[:BUYS {amount: 3}]->(tomatoes),
         (matt)-[:BUYS {amount: 2}]->(kale),
         (matt)-[:BUYS {amount: 1}]->(cucumber),

         (jeff)-[:BUYS {amount: 3}]->(cookies),
         (jeff)-[:BUYS {amount: 2}]->(milk),

         (brie)-[:BUYS {amount: 1}]->(tomatoes),
         (brie)-[:BUYS {amount: 2}]->(milk),
         (brie)-[:BUYS {amount: 2}]->(kale),
         (brie)-[:BUYS {amount: 3}]->(cucumber),
         (brie)-[:BUYS {amount: 0.3}]->(celery),

         (elsa)-[:BUYS {amount: 3}]->(chocolate),
         (elsa)-[:BUYS {amount: 3}]->(milk)
    """
)

# We define how we want to project our database into GDS
node_projection = ["Person", "Product"]
relationship_projection = {"BUYS": {"orientation": "UNDIRECTED", "properties": "amount"}}

# Before actually going through with the projection, let's check how much memory is required
result = gds.graph.project.estimate(node_projection, relationship_projection)

print(f"Required memory for native loading: {result['requiredMemory']}")