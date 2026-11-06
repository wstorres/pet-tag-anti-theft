import json
import logging
import datetime
import os
import uuid
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
PETS_TABLE_NAME = os.environ.get('PETS_TABLE', 'pet-tag-anti-theft-pets-dev')
TAGS_TABLE_NAME = os.environ.get('TAGS_TABLE', 'pet-tag-anti-theft-tags-dev')

def lambda_handler(event, context):
    """
    Cadastra o perfil do pet e vincula a tag comprada ao animal,
    validando previamente se a tag é autorizada (Whitelist) e está VIRGIN.
    """
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Formato JSON inválido."})
        }
    
    tag_id = body.get('tag_id')
    pet_name = body.get('pet_name')
    species = body.get('species', 'Cão')
    owner_name = body.get('owner_name')
    owner_phone = body.get('owner_phone')
    owner_email = body.get('owner_email')
    medical_notes = body.get('medical_notes', '')
    
    if not tag_id or not pet_name or not owner_phone:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Campos obrigatórios: tag_id, pet_name e owner_phone."})
        }
    
    pets_table = dynamodb.Table(PETS_TABLE_NAME)
    tags_table = dynamodb.Table(TAGS_TABLE_NAME)
    
    try:
        # 1. Trava de Segurança: Verificar se a Tag existe na Whitelist de Fabricação
        tag_response = tags_table.get_item(Key={"tag_id": tag_id})
        tag_item = tag_response.get("Item")
        
        if not tag_item:
            logger.warning(f"Tentativa de cadastro com tag não autorizada/inexistente: {tag_id}")
            return {
                "statusCode": 403,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Tag inválida ou não autorizada pelo fabricante."})
            }
        
        # 2. Verificar se a tag já foi ativada anteriormente
        if tag_item.get("status") != "VIRGIN":
            logger.warning(f"Tentativa de reutilização de tag já ativa: {tag_id}")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Esta tag já se encontra ativa ou bloqueada no sistema."})
            }
        
        # 3. Processo de Cadastro
        pet_id = f"pet_{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.utcnow().isoformat()
        
        pet_item = {
            "pet_id": pet_id,
            "tag_id": tag_id,
            "pet_name": pet_name,
            "species": species,
            "owner_name": owner_name,
            "owner_phone": owner_phone,
            "owner_email": owner_email,
            "medical_notes": medical_notes,
            "is_lost": False,
            "created_at": created_at
        }
        
        # Atualiza o status da tag para ACTIVE e vincula ao pet
        updated_tag_item = {
            "tag_id": tag_id,
            "status": "ACTIVE",
            "bound_pet_id": pet_id,
            "updated_at": created_at
        }
        
        # Salva as informações nas respectivas tabelas
        pets_table.put_item(Item=pet_item)
        tags_table.put_item(Item=updated_tag_item)
        
        logger.info(f"Pet {pet_name} cadastrado com sucesso e tag {tag_id} ativada.")
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "message": "Pet cadastrado e tag ativada com segurança!",
                "pet_id": pet_id,
                "tag_id": tag_id
            })
        }
        
    except Exception as e:
        logger.error(f"Erro crítico ao processar o cadastro: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Erro interno ao processar o cadastro na nuvem."})
        }