from square.client import Client
import uuid
import datetime
from datetime import datetime, timedelta



# Create an instance of the API Client 
# and initialize it with the credentials 
# for the Square account whose assets you want to manage



client = Client(
    access_token='EAAAETVdrVxmx1MSRmMiKcJcMxbaKT4bqdyp9W9u7eUjGy8whckEzYYzFVWdECEP',
    environment='production',
)



 
def add_to_square(name, sku_upc, price, employee, stock):
    # Create a unique key for this creation operation so you don't accidentally
    # create the customer multiple times if you need to retry this operation.
    idempotency_key = str(uuid.uuid1())
    variation_id = '#' + str(uuid.uuid4())
    id =  '#' + str(uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org'))


    if('.' in price):
        price = price.replace('.', '')
    if('$' in price):
        price = price.replace('$', '')


    result = client.catalog.upsert_catalog_object(
    body = {
        "idempotency_key": idempotency_key,
        "object": {
        "type": "ITEM",
        "id": id,
        "item_data": {
            "name": name,
            "description": "Add Some description",
            "variations": [
            {
                "type": "ITEM_VARIATION",
                "id": variation_id,
                "item_variation_data": {
                "item_id": id,
                "sku": sku_upc,
                "upc": sku_upc,
                "pricing_type": "FIXED_PRICING",
                "price_money": {
                    "amount": int(price),
                    "currency": "USD"
                },
                "user_data": employee,
                "location_overrides": [
                    {
                    "location_id": "CZCBF92P4G7WZ"
                    }
                ]
                }
            }
            ],
            "product_type": "REGULAR",
            "ecom_visibility": "UNINDEXED"
        }
        }
    }
    )

    if result.is_success():
        #print(result.body)
        pass
    elif result.is_error():
        print("ERROR")
        print(result.errors)
        return False
    
    
    catalog_object = result.body['catalog_object']['item_data']['variations']
    catalog_object_id = str(catalog_object[0]['id'])

    #time.sleep(1)
    timestamp = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
    #d = datetime.today() - timedelta(days=1)
    #timestamp = d.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(timestamp)

    result1 = client.inventory.batch_change_inventory(
    body = {
        "idempotency_key": idempotency_key,
        "changes": [
        {
            "type": "ADJUSTMENT",
            "adjustment": {
            "from_state": "NONE",
            "to_state": "IN_STOCK",
            "location_id": "CZCBF92P4G7WZ",
            "catalog_object_id": catalog_object_id,
            "quantity": stock,
            "occurred_at": timestamp

            }
        }
        ]
    }
    )
    
    if result1.is_success():
        return True
    elif result1.is_error():
        print("ERROR")
        print(result1.errors)
        return False
