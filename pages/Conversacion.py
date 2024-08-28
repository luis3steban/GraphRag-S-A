import streamlit as st

from graphrag import GraphRAGChain, GraphRAGText2CypherChain
from ui_utils import render_header_svg, get_neo4j_url_from_uri

NORTHWIND_NEO4J_URI = st.secrets['NORTHWIND_NEO4J_URI']
NORTHWIND_NEO4J_USERNAME = st.secrets['NORTHWIND_NEO4J_USERNAME']
NORTHWIND_NEO4J_PASSWORD = st.secrets['NORTHWIND_NEO4J_PASSWORD']

st.set_page_config(page_icon="images/logo-mark-fullcolor-RGB-transBG.svg", layout="wide")
render_header_svg("images/stack.svg", 200)
render_header_svg("images/bottom-header.svg", 200)
st.markdown(' ')
with st.expander('GEMELO SOCIOS&AMIGOS INFO:'):
    st.markdown('''####  Socios&Amigos: Datos de encuestas y premiaciones de exportación/importación de productos farmaceuticos.
    ''')
    st.image('images/image.png', width=800,use_column_width=True)
    st.markdown(
        f'''Usa la siguiente consulta en [Neo4j Browser]({get_neo4j_url_from_uri(NORTHWIND_NEO4J_URI)}) to explore the data:''')
    st.code('CALL db.schema.visualization()', language='cypher')

prompt_instructions_with_schema = '''#Context 
RESPONTE EN ESPAÑOL
asegurate de no mandar texto en tu solucion y solo codigo cypher , solo puedes ejecutar una RETURN en la sintaxis de cypher.
Actua como un experto en cypher de neo4j y de acuerdo al siguiente esquema del modelo de datos del grafo, escribe consultas validas en cypher. 
en base al contexto que generas de lo que te pido respondete a su sugerencia.
No se puede usar la agregación en ORDER BY si no hay expresiones agregadas en el WITH.
Solo usa `WHERE` para condiciones basadas en propiedades de nodos y no para relaciones ya coincidentes.
para realizar una busqueda
importante que si quieres hacer la busqueda de un valor de la propiedad de un nodo o relacion insertes el valor en mayusculas
no agreges comillas para mandar el cypher.
::Usa ORDER BY para ordenar los resultados basados en una propiedad o en una expresión agregada que esté presente en la cláusula RETURN.
Asegúrate de que cualquier columna utilizada en `ORDER BY` esté incluida en `RETURN`.
SINTAXIS DE EJEMPLO:
MATCH (p:Producto)<-[:PRODUCTO_DISPONIBLE]-(c:Cliente)-[:ESTA_EN]->(m:Municipio)
WHERE m.nombre = 'BOGOTA'
RETURN DISTINCT p.nombre_producto AS ProductoMasDisponible , COUNT(p) AS ORDEN 
ORDER BY ORDEN DESC
Usa las siguientes Etiquetas y propiedades de nodo para crear el cypher

["Respuesta"], ["respuesta"]
["Encuesta"], ["nombre"]
["Pregunta"], ["Pregunta"]
["Cliente"], ["Celular_Aut_Movii", "Tel_moovi", "Dueño_PDV", "Contacto_vm", "estado", "id_cliente", "Dueño_PDV_ci", "Cajones", "coordenadas", "Nombre_Aut_Movii", "Cedula_Aut_Movii", "nombre_cliente"]
["Agente"], ["nombre_agente", "id_agente"]
["Gerente"], ["id_gerente", "nombre_gerente"]
["Premio"], ["accion", "movii", "valor", "id_transaction", "id_premio"]
["Municipio"], ["nombre"]
["Region"], ["textEmbedding", "text", "combinedText", "nombre"]
["Categoria"], ["categoria"]
["Puntaje"], ["puntaje"]
["Producto"], ["nombre_producto"]

Rutas de recorrido de gráficos aceptadas

(:Respuesta)-[:RESPUESTA]->(:Pregunta), 
(:Cliente)-[:RESPONDE]->(:Respuesta),
(:Cliente)-[:REALIZA]->(:Encuesta),
(:Cliente)-[:PERTENECE]->(:Categoria), 
(:Municipio)-[:DENTRO_DE]->(:Region), 
(:Cliente)-[:TIENE_PREMIO]->(:Premio)
(:Cliente)-[:ESTA_EN]->(:Municipio)
(:Agente)-[:GESTIONA]->(:Premio)
(:Agente)-[:VALIDA]->(:Encuesta)
(:Encuesta)-[:TIENE]->(:Pregunta)
(:Encuesta)-[:TIENE_PUNTAJE]->(:Puntaje)
(:Agente)-[:REPORTA]->(:Gerente)
(:Cliente)-[:PRODUCTO_DISPONIBLE]->(:Producto)
(:Cliente)-[:STOCK_AGOTADO]->(:Producto)

importante que si quieres hacer la busqueda de un valor de la propiedad de un nodo o relacion insertes el valor en mayusculas
'''

prompt_instructions_vector_only = """La primera importante responde en español. Eres un experto en productos y ventas al por menor que puede responder preguntas basándose únicamente en el contexto proporcionado a continuación.
* Responde la pregunta ESTRICTAMENTE basándote en el contexto proporcionado en el JSON a continuación.
* No asumas ni recuperes información fuera del contexto.
* Piensa paso a paso antes de responder.
* No devuelvas texto útil o adicional ni disculpas.
* Enumera los resultados en formato de texto enriquecido si hay más de un resultado.
 """

top_k_vector_only = 5
vector_index_name = 'region_text_embeddings'

vector_only_rag_chain = GraphRAGChain(
    neo4j_uri=NORTHWIND_NEO4J_URI,
    neo4j_auth=(NORTHWIND_NEO4J_USERNAME, NORTHWIND_NEO4J_PASSWORD),
    vector_index_name=vector_index_name,
    prompt_instructions=prompt_instructions_vector_only,
    k=top_k_vector_only)

graphrag_t2c_chain = GraphRAGText2CypherChain(
    neo4j_uri=NORTHWIND_NEO4J_URI,
    neo4j_auth=(NORTHWIND_NEO4J_USERNAME, NORTHWIND_NEO4J_PASSWORD),
    prompt_instructions=prompt_instructions_with_schema,
    properties_to_remove_from_cypher_res=['textEmbedding'])

prompt = st.text_input("Escribe tu consulta:", value="")


if prompt:
    with st.spinner('Running GraphRAG...'):
        with st.expander('__Respuesta:__', True):
            st.markdown(graphrag_t2c_chain.invoke(prompt))
        st.success('Listo!')

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

""", unsafe_allow_html=True)
