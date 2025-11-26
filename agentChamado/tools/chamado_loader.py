import json
import os

def get_chamado_mock(chamado_id: str = "CH-2024-001") -> dict:
    """
    Recupera os dados de um chamado de suporte.
    
    Args:
        chamado_id: O ID do chamado a ser recuperado. (Neste mock, sempre retorna o mesmo exemplo se não encontrado)
    
    Returns:
        dict: Um dicionário contendo os dados do chamado (ID, Módulo, Mensagens).
    """
    # Caminho para o arquivo mock
    # Assumindo que este script está em agentChamado/tools/
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_path, "data", "chamado_mock.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # O JSON agora é uma lista de chamados. Vamos procurar pelo ID.
        if isinstance(data, list):
            # Tenta encontrar o chamado exato
            for chamado in data:
                if str(chamado.get("Chamado")) == str(chamado_id):
                    return chamado
            
            # Se não encontrar e tiver dados, retorna o primeiro como exemplo/mock
            if data:
                return data[0]
            else:
                return {"error": "Lista de chamados vazia no mock."}
        
        # Fallback para estrutura antiga (objeto único)
        elif isinstance(data, dict):
            if chamado_id:
                 data["Chamado"] = chamado_id
            return data
            
        return {"error": "Formato de JSON inválido."}

    except FileNotFoundError:
        return {"error": f"Arquivo de dados mock não encontrado em {json_path}"}
    except Exception as e:
        return {"error": f"Erro ao ler dados do chamado: {str(e)}"}
