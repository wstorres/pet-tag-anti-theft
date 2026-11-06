import boto3
import datetime
import os

# Configuração local ou ambiente (ajuste o region se necessário)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
TAGS_TABLE_NAME = os.environ.get('TAGS_TABLE', 'pet-tag-anti-theft-tags-dev')

def seed_initial_batch(start_index=1, end_index=100):
    """
    Gera e insere um lote inicial de tags virgens na tabela do DynamoDB.
    Ex: TAG-001 até TAG-100
    """
    table = dynamodb.Table(TAGS_TABLE_NAME)
    print(f"Iniciando carga de tags na tabela {TAGS_TABLE_NAME}...")
    
    for i in range(start_index, end_index + 1):
        tag_id = f"TAG-{i:03d}"
        item = {
            "tag_id": tag_id,
            "status": "VIRGIN",
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        try:
            table.put_item(Item=item)
            print(f"[SUCESSO] Tag inserida: {tag_id}")
        except Exception as e:
            print(f"[ERRO] Falha ao inserir {tag_id}: {str(e)}")
            
    print("Carga de lote concluída!")

if __name__ == "__main__":
    # Exemplo: Criar 100 tags iniciais para testes
    seed_initial_batch(1, 100)