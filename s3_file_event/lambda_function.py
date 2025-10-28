import json
import boto3
import os
import urllib.parse
from datetime import datetime
import uuid  # <-- 1. Importamos la librería UUID

TABLE_NAME = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # 1. Obtener datos del evento S3 (más detallados)
        record = event['Records'][0] # Obtenemos el registro completo
        s3_record = record['s3']
        
        # Datos del archivo
        bucket_name = s3_record['bucket']['name']
        image_id = urllib.parse.unquote_plus(s3_record['object']['key'], encoding='utf-8') # Esta es la clave de partición
        object_size = s3_record['object']['size']
        
        # Metadatos del evento (como en tu ejemplo)
        event_time = record['eventTime']
        event_name = record['eventName']
        region = record['awsRegion']

        print(f"Procesando: {image_id} del bucket {bucket_name}")

        # 2. Preparar el item para DynamoDB
        item_to_save = {
            'image_id': image_id,  # Clave de partición (Requerida por la evaluación)
            'fileid': str(uuid.uuid4()), # <-- 2. ¡AQUÍ ESTÁ TU ID ÚNICO!
            'bucket': bucket_name,
            'size_bytes': object_size,
            's3_timestamp': event_time,
            'event_name': event_name,
            'aws_region': region,
            'processed_at': datetime.utcnow().isoformat()
        }

        # 3. Guardar en DynamoDB
        table.put_item(Item=item_to_save)
        return {'statusCode': 200, 'body': json.dumps('Metadatos guardados.')}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'Error al procesar: {e}')}