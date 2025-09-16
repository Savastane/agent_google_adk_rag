from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import vector_search, graph_search, document_processor


def create_rag_agent() -> Agent:
    """Creates the RAG agent with vector and graph search tools."""

    vector_search_tool = FunctionTool(
        fn=vector_search.search,
        description="Busca por documentos relevantes no banco de dados vetorial. Pode ser opcionalmente filtrado por 'assunto'.
    )
    graph_search_tool = FunctionTool(
        fn=graph_search.search,
        description="Busca por entidades e relacionamentos no banco de dados de grafos."
    )
    remove_document_tool = FunctionTool(
        fn=document_processor.remove_document,
        description="Remove um documento da base de conhecimento a partir de seu ID."
    )

    # The system prompt tells the agent how to behave.
    # It can be used to provide context, instructions, and personality.
    system_prompt = (
        "Você é um assistente prestativo que responde a perguntas usando uma combinação de busca "
        "em banco de dados vetorial e de grafos. Você também pode remover documentos da base de conhecimento. "
        "Ao pesquisar, primeiro, use a busca vetorial para encontrar documentos "
        "relevantes. Em seguida, use a busca de grafos para encontrar entidades e "
        "relacionamentos relacionados. Por fim, sintetize as informações de ambas as fontes para "
        "fornecer uma resposta abrangente."
    )

    return Agent(
        tools=[vector_search_tool, graph_search_tool, remove_document_tool],
        system_prompt=system_prompt,
    )


rag_agent = create_rag_agent()
