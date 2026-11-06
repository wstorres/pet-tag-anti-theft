import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
PETS_TABLE_NAME = os.environ.get('PETS_TABLE', 'pet-tag-anti-theft-pets-dev')
TAGS_TABLE_NAME = os.environ.get('TAGS_TABLE', 'pet-tag-anti-theft-tags-dev')

def lambda_handler(event, context):
    """
    Retorna as informações públicas do pet para exibição no celular de quem escaneou a tag,
    juntamente com o aviso jurídico ostensivo anti-apropriação.
    """
    path_parameters = event.get('pathParameters', {}) or {}
    tag_id = path_parameters.get('tag_id')
    
    if not tag_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Parâmetro tag_id é obrigatório."})
        }
    
    tags_table = dynamodb.Table(TAGS_TABLE_NAME)
    pets_table = dynamodb.Table(PETS_TABLE_NAME)
    
    try:
        # 1. Buscar a Tag
        tag_res = tags_table.get_item(Key={"tag_id": tag_id})
        tag_item = tag_res.get("Item")
        
        if not tag_item or tag_item.get("status") != "ACTIVE":
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "status": "unbound",
                    "message": "Esta tag ainda não foi ativada por um tutor."
                })
            }
        
        # 2. Buscar o Pet vinculado
        pet_id = tag_item.get("bound_pet_id")
        pet_res = pets_table.get_item(Key={"pet_id": pet_id})
        pet_item = pet_res.get("Item")
        
        if not pet_item:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Cadastro de pet não encontrado para esta tag."})
            }
        
        # 3. Filtrar apenas os dados públicos (Proteção de Privacidade)
        public_profile = {
            "pet_name": pet_item.get("pet_name"),
            "species": pet_item.get("species"),
            "owner_name": pet_item.get("owner_name"),
            "owner_phone": pet_item.get("owner_phone"),
            "medical_notes": pet_item.get("medical_notes", ""),
            "is_lost": pet_item.get("is_lost", False),
            "legal_notice": "AVISO LEGAL: Este animal possui tutor registrado. A não devolução imediata ou posse não autorizada pode configurar crime de Apropriação Indébita (Art. 169 do Código Penal)."
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "pet": public_profile
            })
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfil do pet: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Erro ao consultar dados do pet."})
        }