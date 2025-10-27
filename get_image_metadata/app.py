import json
import boto3
import os
from decimal import Decimal

# Helper para convertir Decimales de DynamoDB a JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

TABLE_NAME = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
        # En HTTP API, el método está en esta ruta
        http_method = event['requestContext']['http']['method']
        # -------------------------------------
        
        path_parameters = event.get('pathParameters')

        # CASO 1: GET /metadata (Listar todo)
        if http_method == 'GET' and not path_parameters:
            response = table.scan()
            items = response.get('Items', [])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(items, cls=DecimalEncoder)
            }

        # Si hay pathParameters, debe existir 'image_id'
        if path_parameters and 'image_id' in path_parameters:
            image_id = path_parameters['image_id']

            # CASO 2: GET /metadata/{image_id} (Obtener uno)
            if http_method == 'GET':
                response = table.get_item(Key={'image_id': image_id})
                item = response.get('Item')
                if item:
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(item, cls=DecimalEncoder)
                    }
                else:
                    return {'statusCode': 404, 'body': json.dumps('Item no encontrado')}

            # CASO 3: DELETE /metadata/{image_id} (Borrar uno)
            elif http_method == 'DELETE':
                table.delete_item(Key={'image_id': image_id})
                return {'statusCode': 200, 'body': json.dumps('Item eliminado')}

        return {'statusCode': 400, 'body': json.dumps('Ruta o método no válido')}
    
    except Exception as e:
        print(f"Error: {e}")
        # Este es el error que estás viendo:
        return {'statusCode': 500, 'body': json.dumps(f'Error en el servidor: {str(e)}')}