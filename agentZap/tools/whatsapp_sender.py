import requests
import json

# Configurações da API baseadas na imagem fornecida
# Em produção, estas variáveis devem vir de variáveis de ambiente
API_URL = "https://zap.redecity.com.br/message/sendText/A25bf5df2aebf4d32bef128b12f180629"
API_KEY = "A25bf5df2aebf4d32bef128b12f180629"

def enviar_mensagem_whatsapp(numero: str, mensagem: str) -> str:
    """
    Envia uma mensagem de texto via WhatsApp usando a API iZap.
    
    Args:
        numero (str): O número de telefone do destinatário (ex: '5571988383587'). 
                      Deve incluir o código do país e DDD, apenas números.
        mensagem (str): O texto da mensagem a ser enviada.
        
    Returns:
        str: Resultado da operação (sucesso ou erro).
    """
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero,
        "text": mensagem
    }
    
    print(f"Enviando WhatsApp para {numero}...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200 or response.status_code == 201:
            return f"Mensagem enviada com sucesso! Resposta da API: {response.text}"
        else:
            return f"Falha ao enviar mensagem. Status: {response.status_code}. Erro: {response.text}"
            
    except Exception as e:
        return f"Erro ao conectar com a API de WhatsApp: {str(e)}"
