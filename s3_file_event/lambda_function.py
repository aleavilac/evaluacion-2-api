import json
import boto3
import os
import urllib.parse
from datetime import datetime

# Lee el nombre de la tabla desde la variable de entorno
TABLE_NAME = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # 1. Obtener datos del evento S3
        s3_record = event['Records'][0]['s3']
        bucket_name = s3_record['bucket']['name']

        # El 'image_id' será el nombre/key del archivo
        image_id = urllib.parse.unquote_plus(s3_record['object']['key'], encoding='utf-8')
        object_size = s3_record['object']['size']
        event_time = event['Records'][0]['eventTime']

        print(f"Procesando: {image_id} del bucket {bucket_name}")

        # 2. Preparar el item (usando 'image_id' como clave)
        item_to_save = {
            'image_id': image_id,
            'bucket': bucket_name,
            'size_bytes': object_size,
            's3_timestamp': event_time,
            'processed_at': datetime.utcnow().isoformat()
        }

        # 3. Guardar en DynamoDB
        table.put_item(Item=item_to_save)
        return {'statusCode': 200, 'body': json.dumps('Metadatos guardados.')}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'Error al procesar: {e}')}