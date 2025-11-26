from google.adk.agents import Agent
from .tools import whatsapp_sender

root_agent = Agent(
    name="agentZap",
    model="gemini-2.0-flash",
    description="Um agente especializado em comunicação e envio de notificações via WhatsApp.",
    instruction=(
        "Você é um assistente de comunicação responsável por notificar usuários via WhatsApp. "
        "Sua principal função é receber textos ou resumos e enviá-los para os números de telefone especificados. "
        "Ao enviar uma mensagem, certifique-se de que o texto esteja formatado de forma clara e concisa, "
        "ideal para leitura em dispositivos móveis. "
        "Sempre confirme o envio da mensagem."
    ),
    tools=[whatsapp_sender.enviar_mensagem_whatsapp]
)
