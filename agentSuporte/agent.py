import os

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import vector_search, graph_search, document_processor, kcs_tool
from agentZap.tools import whatsapp_sender

# Configure the Gemini API key
#genai.configure(api_key=os.environ["GEMINI_API_KEY"])



# def create_rag_agent() -> Agent:
#     """Creates the RAG agent with vector and graph search tools."""

#     vector_search_tool = FunctionTool(
#         fn=vector_search.search,
#         description="Busca por documentos relevantes no banco de dados vetorial. Pode ser opcionalmente filtrado por 'assunto'.
#     )
#     graph_search_tool = FunctionTool(
#         fn=graph_search.search,
#         description="Busca por entidades e relacionamentos no banco de dados de grafos."
#     )
#     remove_document_tool = FunctionTool(
#         fn=document_processor.remove_document,
#         description="Remove um documento da base de conhecimento a partir de seu ID."
#     )

    # The system prompt tells the agent how to behave.
    # It can be used to provide context, instructions, and personality.
    # The system prompt tells the agent how to behave.
    # It can be used to provide context, instructions, and personality.
    # system_prompt = (
    #     "Você é um assistente prestativo que responde a perguntas usando uma combinação de busca "
    #     "em banco de dados vetorial e de grafos. Você também pode remover documentos da base de conhecimento. "
    #     "Ao pesquisar, primeiro, use a busca vetorial para encontrar documentos "
    #     "relevantes. Em seguida, use a busca de grafos para encontrar entidades e "
    #     "relacionamentos relacionados. Por fim, use o modelo de linguagem (Gemini) para sintetizar as informações de ambas as fontes e "
    #     "fornecer uma resposta abrangente e bem elaborada em português."
    # )

    # llm = genai.GenerativeModel('gemini-2.0-flash')

    # return Agent(
    #     tools=[vector_search_tool, graph_search_tool, remove_document_tool],
    #     llm=llm,
    #     system_prompt=system_prompt,
    # )


root_agent = Agent(
    name="agentSuporte",
    model="gemini-2.0-flash",
    description="Um agente de suporte ao cliente  que usa RAG com bancos de dados vetoriais e de grafos. ultilizado por funcionarios da empresa ADN",
    instruction=(
        "sempre que der alguma responsta informe que você é um agente de suporte ao cliente"
        "Você é um assistente prestativo que responde a perguntas usando uma combinação de busca "
        "mostre os parameros de pesquisa no vetorial e no graph"
        "acrescente no contexto a empresa ADN"
        "nos bancos de dados vetorial e de grafos. Sua resposta deve ser baseada SOMENTE nas informações retornadas pelas ferramentas de busca. "        
        "Não use conhecimento externo. Primeiro, use a busca vetorial para encontrar documentos relevantes. Em seguida, use a busca de grafos para encontrar entidades e relacionamentos. "
        "Por fim, sintetize as informações de ambas as fontes para fornecer uma resposta abrangente e bem elaborada em português."
        "Você também possui uma ferramenta especializada para gerar artigos de conhecimento KCS a partir de números de chamados. Se o usuário pedir para analisar um chamado ou gerar um artigo, use a ferramenta 'gerar_artigo_kcs'."
        "Além disso, você tem a capacidade de enviar mensagens para o WhatsApp. Se solicitado a enviar um resumo de chamado ou qualquer informação para um número de telefone, use a ferramenta 'enviar_mensagem_whatsapp'."
    ),
    tools=[vector_search.vectorsearch, graph_search.graphsearch, kcs_tool.gerar_artigo_kcs, whatsapp_sender.enviar_mensagem_whatsapp]
)

#rag_agent = create_rag_agent()
