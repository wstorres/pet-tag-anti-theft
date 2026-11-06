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
    Cadastra o perfil do pet e vincula a tag comprada ao animal.
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
    
    pet_id = f"pet_{uuid.uuid4().hex[:8]}"
    created_at = datetime.datetime.utcnow().isoformat()
    
    pets_table = dynamodb.Table(PETS_TABLE_NAME)
    tags_table = dynamodb.Table(TAGS_TABLE_NAME)
    
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
    
    tag_item = {
        "tag_id": tag_id,
        "status": "ACTIVE",
        "bound_pet_id": pet_id,
        "updated_at": created_at
    }
    
    try:
        pets_table.put_item(Item=pet_item)
        tags_table.put_item(Item=tag_item)
        
        logger.info(f"Pet {pet_name} cadastrado com sucesso e vinculado à tag {tag_id}")
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "message": "Pet cadastrado e tag ativada com sucesso!",
                "pet_id": pet_id,
                "tag_id": tag_id
            })
        }
    except Exception as e:
        logger.error(f"Erro ao cadastrar pet no DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Erro ao salvar no banco de dados."})
        }