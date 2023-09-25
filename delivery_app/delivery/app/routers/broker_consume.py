import pika
import requests

def callback(ch, method, properties, body):
    # Imprime el mensaje recibido desde el broker
    print(f" [x] {body}")
    # TODO
    # Realiza una solicitud GET a otro ORDER
    try:
        response = requests.get('/order/{id}', params={'parametro': 'valor'})

        # Verifica si la solicitud fue exitosa
        if response.status_code == 200:
            # Procesa la respuesta del microservicio
            data = response.json()  # Si la respuesta es JSON
            # Realiza las operaciones necesarias con los datos obtenidos
            print("Datos recibidos de order:", data)

        else:
            print(f"La solicitud GET a ORDER falló con el código de estado: {response.status_code}")

    except Exception as e:
        print("Error al realizar la solicitud GET:", str(e))


#COPIADO DE LA PÁGINA DE TUTORIALES DE RABBITMQ:
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()






