import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_security_alert(owner_contact, tag_id, pet_name, geo_info):
    """
    Envia alerta imediato ao tutor quando a tag do pet é escaneada.
    Pode ser integrado com serviços como Resend (E-mail), AWS SNS ou Webhook do WhatsApp.
    """
    cidade = geo_info.get("city", "Localização não identificada")
    regiao = geo_info.get("region", "")
    ip = geo_info.get("ip", "Desconhecido")
    
    mensagem = (
        f"🚨 ALERTA DE SEGURANÇA - SAFEPET ID 🚨\n\n"
        f"A tag do pet '{pet_name}' (ID: {tag_id}) foi escaneada!\n"
        f"📍 Cidade aproximada: {cidade} - {regiao}\n"
        f"🌐 IP do Leitor: {ip}\n"
        f"⏰ Horário: Registrado na nuvem.\n\n"
        f"Acesse o painel para ver mais detalhes."
    )
    
    logger.info(f"ENVIANDO ALERTA PARA {owner_contact}:\n{mensagem}")
    
    # Exemplo de integração via Webhook/API (substitua com as credenciais reais no futuro)
    # response = requests.post("https://api.seu-servico.com/send", json={"to": owner_contact, "message": mensagem})
    
    return True