import sys
import os
import traceback

# Define o caminho raiz explicitamente
ROOT_DIR = r"D:\_lab\python\rag1"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

print(f"Caminho adicionado ao sys.path: {ROOT_DIR}")
print(f"Conteúdo de {ROOT_DIR}:")
try:
    print(os.listdir(ROOT_DIR))
except Exception as e:
    print(f"Erro ao listar diretório: {e}")

print("\nTentando importar AgentRH.agent (case sensitive match)...")

try:
    from AgentRH import agent
    print("Módulo AgentRH.agent importado com sucesso!")
    
    if hasattr(agent, 'root_agent'):
        print("root_agent encontrado no módulo!")
        print(f"Tipo do root_agent: {type(agent.root_agent)}")
    else:
        print("ERRO: root_agent NÃO encontrado no módulo AgentRH.agent")
        print("Atributos disponíveis:", dir(agent))
        
except ImportError:
    print("Falha ao importar AgentRH. Tentando agentRH (lowercase)...")
    try:
        from agentRH import agent
        print("Módulo agentRH.agent importado com sucesso!")
        if hasattr(agent, 'root_agent'):
            print("root_agent encontrado no módulo!")
        else:
            print("ERRO: root_agent NÃO encontrado no módulo agentRH.agent")
    except Exception as e:
        print(f"Erro ao importar agentRH: {e}")
        traceback.print_exc()

except Exception as e:
    print("\n--- ERRO DURANTE A IMPORTAÇÃO ---")
    print(f"Erro: {e}")
    traceback.print_exc()
