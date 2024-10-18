import json
import base64
from kafka import KafkaConsumer, KafkaProducer
from PIL import Image
import torch
import torchvision.transforms as transforms
from io import BytesIO

CIFAR10_LABELS = [
    'airplane', 'automobile', 'bird', 'cat', 'deer', 
    'dog', 'frog', 'horse', 'ship', 'truck'
]

consumer = KafkaConsumer(
    'iot-topic',
    bootstrap_servers=["192.168.5.36"],  
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),  
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='ml-inference-group'  
)
print("Kafka consumer initialized successfully.")

producer = KafkaProducer(
    bootstrap_servers=["192.168.5.36"],  
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  
)
print("Kafka producer for predictions initialized successfully.")

model = torch.hub.load('chenyaofo/pytorch-cifar-models', 'cifar10_resnet20', pretrained=True)
model.eval()  

preprocess = transforms.Compose([
    transforms.Resize((32, 32)),  
    transforms.ToTensor(),  
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.2010]),  
])

def infer_image(image_base64):
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data)).convert("RGB")  

    input_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():  
        output = model(input_tensor)  
        _, predicted_index = output.max(1)  

    predicted_label = CIFAR10_LABELS[predicted_index.item()]  
    return predicted_label

def send_inference_result_to_database(image_id, predicted_label, producer_id):
    result_data = {
        "ID": image_id,
        "InferredValue": predicted_label
    }
    producer.send('iot-predictions', value=result_data)
    producer.flush()  
    print(f"Sent inference result (with label) for image ID {image_id} to Kafka 'iot-predictions'.")

def send_inference_result_to_producer(image_id, producer_id):
    result_data = {
        "ID": image_id,
        "producer_id": producer_id  
    }
    print(f"Sending result data to producer: {result_data}")  # 打印发送前的数据
    producer.send('time-topic', value=result_data)
    producer.flush()  
    print(f"Sent inference result (ID and producer ID) for image ID {image_id} to Kafka 'time-topic'.")

try:
    for message in consumer:
        data = message.value  
        print(f"Received data from Kafka with ID: {data['ID']}")

        image_base64 = data['Data']  
        producer_id = data['producer_id']  

        predicted_label = infer_image(image_base64)
        print(f"Predicted class for image with ID {data['ID']}: {predicted_label}")

        send_inference_result_to_database(data['ID'], predicted_label, producer_id)  
        send_inference_result_to_producer(data['ID'], producer_id)  

except Exception as e:
    print(f"Error consuming message or performing inference: {e}")
finally:
    consumer.close()
    producer.close()
    print("Kafka consumer and producer closed.")
