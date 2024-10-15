import azure.functions as func
import logging
import json
import os  # Add this import for using os.environ
from azure.cosmos import CosmosClient, exceptions

# Initialize CosmosDB client with your specific details
endpoint = os.environ.get("COSMOS_DB_ENDPOINT")
key = os.environ.get("COSMOS_DB_KEY")
database_name = "saaddb"
container_name = "counter"

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_triggersaad")
def http_triggersaad(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Initialize visitor count variable
    visitor_count = 0

    # Increment the visitor counter
    try:
        visitor_item = container.read_item(item="visitor_count", partition_key="visitor_count")
        visitor_count = visitor_item.get('count', 0)
        visitor_item['count'] = visitor_count + 1
        container.upsert_item(visitor_item)
        visitor_count = visitor_item['count']
    except exceptions.CosmosHttpResponseError:
        # Create the item if it doesn't exist
        visitor_item = {
            'id': 'visitor_count',
            'count': 1,
            'partition_key': 'visitor_count'  # Ensure you have a partition key if needed
        }
        container.create_item(visitor_item)
        visitor_count = 1

    # Process the request for a name
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(
            json.dumps({"message": f"Hello, {name}. Your name has been added to the database.", "visitor_count": visitor_count}),
            status_code=200,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            json.dumps({"message": "This HTTP triggered function executed successfully.", "visitor_count": visitor_count}),
            status_code=200,
            mimetype="application/json"
        )
