import pika
import json

# Create a Python dictionary representing your JSON data
json_data = {
    "order_id": 1,
    "description": "Order for FagorSL",
    "delivery_status": "CREATED",
    "location": "Mondragon"
}

json_data2 = {
    "order_id": 1,
    "description": "Order for FagorSL",
    "delivery_status": "READY",
    "location": "Mondragon"
}

json_data3 = {
    "order_id": 1,
    "description": "Order for FagorSL",
    "delivery_status": "DELIVERED",
    "location": "Mondragon"
}


# Serialize the dictionary to JSON
message_body1 = json.dumps(json_data)
message_body2 = json.dumps(json_data2)

connection_parameters = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()
channel.queue_declare(queue='create_delivery')
channel.queue_declare(queue='update_delivery')

# Publish the JSON messages
channel.basic_publish(exchange='', routing_key='create_delivery', body=message_body1)
channel.basic_publish(exchange='', routing_key='update_delivery', body=message_body2)

print(f'Sent JSON message 1: {message_body1}')
print(f'Sent JSON message 1: {message_body2}')

connection.close()
