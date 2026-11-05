import json
import logging
import datetime
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Função acionada quando uma Tag NFC ou QR Code é escaneado.
    Captura dados passivos e dispara alerta silencioso ao tutor.
    """
    # 1. Obter ID da tag a partir da rota (ex: /p/{tag_id})
    path_parameters = event.get('pathParameters', {})
    tag_id = path_parameters.get('tag_id', 'UNKNOWN')
    
    # 2. Capturar IP e User-Agent do cabeçalho da requisição
    headers = event.get('headers', {})
    source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp') or headers.get('X-Forwarded-For', '').split(',')[0]
    user_agent = headers.get('User-Agent', 'Desconhecido')
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # 3. Consulta rápida de IP Geolocation (Serviço Passivo)
    geo_data = {}
    if source_ip and source_ip != '127.0.0.1':
        try:
            res = requests.get(f"http://ip-api.com/json/{source_ip}?fields=status,country,regionName,city,zip,lat,lon,isp", timeout=2)
            if res.status_code == 200:
                geo_data = res.json()
        except Exception as e:
            logger.error(f"Erro ao consultar GeoIP: {str(e)}")
            
    # 4. Log do Evento de Segurança
    access_log = {
        "tag_id": tag_id,
        "timestamp": timestamp,
        "ip": source_ip,
        "user_agent": user_agent,
        "location": {
            "city": geo_data.get("city", "Não identificada"),
            "region": geo_data.get("regionName", ""),
            "country": geo_data.get("country", ""),
            "isp": geo_data.get("isp", "")
        }
    }
    
    logger.info(f"LOG DE SEGURANÇA REGISTRADO: {json.dumps(access_log)}")
    
    # TODO: Persistir no DynamoDB e disparar notificação para o tutor
    
    # 5. Resposta enviada ao navegador do leitor
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "status": "success",
            "message": "Tag identificada com sucesso",
            "tag_id": tag_id,
            "security_warning": "ANIMAL REGISTRADO E MONITORADO. POSSE NÃO AUTORIZADA CONFIGURA APROPRIAÇÃO INDÉBITA (Art. 169 do CP).",
            "log_registered": True
        })
    }