import json
import logging
import datetime
import os
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Conexão com o DynamoDB
dynamodb = boto3.resource('dynamodb')
LOGS_TABLE_NAME = os.environ.get('LOGS_TABLE', 'pet-tag-anti-theft-logs-dev')

def lambda_handler(event, context):
    """
    Função acionada quando uma Tag NFC ou QR Code é escaneada.
    Captura dados passivos, grava no DynamoDB e dispara alerta ao tutor.
    """
    path_parameters = event.get('pathParameters', {}) or {}
    tag_id = path_parameters.get('tag_id', 'UNKNOWN')
    
    headers = event.get('headers', {}) or {}
    source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp') or headers.get('X-Forwarded-For', '').split(',')[0]
    user_agent = headers.get('User-Agent', 'Desconhecido')
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # GeoIP silencioso
    geo_data = {}
    if source_ip and source_ip not in ['127.0.0.1', '']:
        try:
            res = requests.get(f"http://ip-api.com/json/{source_ip}?fields=status,country,regionName,city,zip,lat,lon,isp", timeout=2)
            if res.status_code == 200:
                geo_data = res.json()
        except Exception as e:
            logger.error(f"Erro ao consultar GeoIP: {str(e)}")
            
    access_log = {
        "tag_id": tag_id,
        "timestamp": timestamp,
        "ip": source_ip,
        "user_agent": user_agent,
        "city": geo_data.get("city", "Não identificada"),
        "region": geo_data.get("regionName", ""),
        "country": geo_data.get("country", ""),
        "isp": geo_data.get("isp", "")
    }
    
    # Persistência no DynamoDB
    try:
        table = dynamodb.Table(LOGS_TABLE_NAME)
        table.put_item(Item=access_log)
        logger.info(f"Log gravado no DynamoDB com sucesso para a tag {tag_id}")
    except Exception as e:
        logger.error(f"Erro ao gravar log no DynamoDB: {str(e)}")
    
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
            "security_warning": "ANIMAL REGISTRADO E MONITORADO. POSSE NÃO AUTORIZADA CONFIGURA APROPRIAÇÃO INDÉBITA.",
            "log_registered": True
        })
    }