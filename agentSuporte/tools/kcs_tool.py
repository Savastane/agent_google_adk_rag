import os
from agentChamado.tools.chamado_loader import get_chamado_mock
from agentChamado.agent import root_agent as kcs_agent
import google.generativeai as genai

# Configura a API Key se disponível no ambiente, caso contrário assume que o ambiente já tem credenciais
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def gerar_artigo_kcs(chamado_id: str) -> str:
    """
    Aciona o Agente Especialista em KCS para analisar um chamado e gerar um artigo de conhecimento.
    
    Args:
        chamado_id (str): O número/ID do chamado a ser analisado (ex: 'CH-2024-001').
    
    Returns:
        str: O artigo de conhecimento gerado no formato KCS.
    """
    print(f"Acionando agente KCS para o chamado {chamado_id}...")
    
    # 1. Obter os dados do chamado
    dados_chamado = get_chamado_mock(chamado_id)
    
    if "error" in dados_chamado:
        return f"Erro ao obter chamado: {dados_chamado['error']}"
    
    # 2. Preparar o prompt combinando a persona do agente KCS com os dados
    # O kcs_agent.instruction contém todas as regras de formatação e comportamento
    prompt_completo = (
        f"{kcs_agent.instruction}\n\n"
        f"--- DADOS DO CHAMADO ---\n"
        f"{dados_chamado}\n"
        f"------------------------\n"
        f"Gere o artigo KCS agora."
    )
    
    try:
        # 3. Invocar o modelo diretamente para simular a execução do agente
        # Usamos o mesmo modelo definido no agente
        model_name = kcs_agent.model
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(prompt_completo)
        return response.text
        
    except Exception as e:
        return f"Erro ao executar o agente KCS: {str(e)}"
