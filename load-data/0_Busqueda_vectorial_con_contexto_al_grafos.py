import streamlit as st

from graphrag import GraphRAGChain
from ui_utils import render_header_svg, get_neo4j_url_from_uri

NORTHWIND_NEO4J_URI = st.secrets['NORTHWIND_NEO4J_URI']
NORTHWIND_NEO4J_USERNAME = st.secrets['NORTHWIND_NEO4J_USERNAME']
NORTHWIND_NEO4J_PASSWORD = st.secrets['NORTHWIND_NEO4J_PASSWORD']

render_header_svg("images/bottom-header.svg", 200)
st.markdown(' ')
with st.expander('Dataset Info:'):
    st.markdown('''####  Socios&Amigos: Datos de encuestas y premiaciones de exportación/importación de productos farmaceuticos.
    ''')
    st.image('images/image.png', width=800,use_column_width=True)
    st.markdown(
        f'''Usa la siguiente consulta en [Neo4j Browser]({get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI)}) to explore the data:''')
    st.code('CALL db.schema.visualization()', language='cypher')


graph_retrieval_query = """WITH node AS product, score 
MATCH (re:Region)-[]-(m:Municipio)<-[:ESTA_EN]-(c:Cliente{estado:true})-[r:STOCK_AGOTADO]->(p:Producto)
WITH re, COUNT(distinct r) AS CLIENTES_STOCK_AGOTADO,score
RETURN 
    re.nombre AS text, 
    CLIENTES_STOCK_AGOTADO,
    score,
    {
        Region: re.nombre, 
        clientes_stock_agotado: CLIENTES_STOCK_AGOTADO
    } AS metadata
ORDER BY CLIENTES_STOCK_AGOTADO DESC

"""

prompt_instructions = """La primera importante responde en español. Eres un experto en productos y ventas al por menor que puede responder preguntas basándose únicamente en el contexto proporcionado a continuación.
* Responde la pregunta ESTRICTAMENTE basándote en el contexto proporcionado en el JSON a continuación.
* No asumas ni recuperes información fuera del contexto.
* Piensa paso a paso antes de responder.
* No devuelvas texto útil o adicional ni disculpas.
* Enumera los resultados en formato de texto enriquecido si hay más de un resultado.
 """

top_k = 5
vector_index_name = 'region_text_embeddings'

vector_only_rag_chain = GraphRAGChain(
    neo4j_uri=NORTHWIND_NEO4J_URI,
    neo4j_auth=(NORTHWIND_NEO4J_USERNAME, NORTHWIND_NEO4J_PASSWORD),
    vector_index_name=vector_index_name,
    prompt_instructions=prompt_instructions,
    k=top_k)

graphrag_chain = GraphRAGChain(
    neo4j_uri=NORTHWIND_NEO4J_URI,
    neo4j_auth=(NORTHWIND_NEO4J_USERNAME, NORTHWIND_NEO4J_PASSWORD),
    vector_index_name=vector_index_name,
    prompt_instructions=prompt_instructions,
    graph_retrieval_query=graph_retrieval_query,
    k=top_k)

prompt = st.text_input("Escribe tu consulta:", value="")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vector Only")
    if prompt:
        with st.spinner('Running Vector Only RAG...'):
            with st.expander('__Response:__', True):
                st.markdown(vector_only_rag_chain.invoke(prompt))
            with st.expander("__Context used to answer this prompt:__"):
                st.json(vector_only_rag_chain.last_used_context)
            with st.expander("__Query used to retrieve context:__"):
                vector_rag_query = vector_only_rag_chain.get_full_retrieval_query(prompt)
                st.markdown(f"""
                This query only uses vector search.  The vector search will return the highest ranking `nodes` based on the vector similarity `score`(for this example we chose `{top_k}` nodes)
                """)
                st.code(vector_rag_query, language='cypher')
                st.markdown('### Visualize Retrieval in Neo4j')
                st.markdown('To explore the results in Neo4j do the following:\n' +
                            f'* Go to [Neo4j Browser]({get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI)}) and enter your credentials\n' +
                            '* Run the above queries')
                st.link_button("Try in Neo4j Browser!", get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI))

            st.success('Done!')

with col2:
    st.subheader("Vector Search & Graph Context")

    if prompt:
        with st.spinner('Running GraphRAG...'):
            with st.expander('__Response:__', True):
                st.markdown(graphrag_chain.invoke(prompt))

            with st.expander("__Context used to answer this prompt:__"):
                st.json(graphrag_chain.last_used_context)

            with st.expander("__Query used to retrieve context:__"):
                graph_rag_query = graphrag_chain.get_full_retrieval_query(prompt)
                st.markdown(f"""The following Cypher query was used to obtain vector results enriched with additional context from the graph. The query initially performs a vector search, returning the highest ranking `nodes` based on their vector similarity `score`. In this example, we selected `{top_k}` nodes. Subsequently, the query performs further graph traversals and aggregation to gather context. You can think of this context as 'metadata,' but with the advantages of real-time collection and the flexibility to use robust patterns.
                """)
                st.code(graph_rag_query, language='cypher')
                st.markdown('### Visualize Retrieval in Neo4j')
                st.markdown('To explore the results in Neo4j do the following:\n' +
                            f'* Go to [Neo4j Browser]({get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI)}) and enter your credentials\n' +
                            '* Run the above queries')
                st.link_button("Try in Neo4j Browser!", get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI))

            st.success('Done!')



st.markdown("---")

st.markdown("""
<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border: none !important;
    font-family: "Source Sans Pro", sans-serif;
    color: rgba(49, 51, 63, 0.6);
    font-size: 0.9rem;
  }

  tr {
    border: none !important;
  }

  th {
    text-align: center;
    colspan: 3;
    border: none !important;
    color: #0F9D58;
  }

  th, td {
    padding: 2px;
    border: none !important;
  }
</style>

<table>

</table>
""", unsafe_allow_html=True)
