
# IoT Data Analytics Pipeline Using Kafka, Docker, and Ansible

This project demonstrates how to deploy a cloud-based IoT data analytics pipeline using Kafka, Docker, and Ansible. It automates the setup of virtual machines (VMs), Kafka, Docker services, and executes image classification tasks using the CIFAR-10 dataset.

## Project Overview

The project is composed of several key components:

- **Producer**: Sends images from the CIFAR-10 dataset to a Kafka topic.
- **Inference Service**: Receives images, performs machine learning inference using a pre-trained ResNet model, and sends the result back to Kafka.
- **Consumer**: Consumes the inference results and calculates the end-to-end latency for each image.
  
The entire system is containerized using Docker, and the setup is automated with Ansible.

## Project Structure

- `producer.py`: Sends images to Kafka and starts a thread to listen for inference results.
- `inference.py`: Performs inference on the received images and sends results to Kafka.
- `consumer.py`: Consumes results from Kafka and handles data processing.
- `docker-compose.yaml`: Defines the Docker services for Kafka, Zookeeper, and the application containers.
- `playbook_master.yaml`: Ansible playbook for setting up VMs and Docker services.
- `Dockerfile`: Dockerfile for building the application image.
- `requirements.txt`: Lists the Python dependencies for the project.

## Prerequisites

- **Ansible**: To automate the setup of VMs and Docker services.
- **Docker & Docker Compose**: To containerize the producer, inference, and Kafka services.
- **Chameleon Cloud**: Or any cloud provider to provision VMs (this setup uses Chameleon).

### Key Features:
- **VM1**: Acts as an IoT data producer, sending CIFAR-10 images to a Kafka broker every 10 seconds.
- **VM2**: Acts as the Kafka broker, facilitating message transmission between producer and consumers.
- **VM3**: Acts as a consumer, performing image classification (machine learning inference) on received images and sending the predictions to a Kafka topic.
- **VM4**: Listens for both raw images and prediction results, storing them in **CouchDB**.

### Tools & Libraries:
- **Apache Kafka**: For message streaming between VMs.
- **PyTorch**: For image classification using pre-trained models.
- **CouchDB**: A NoSQL database to store image data and classification results.
- **Python Libraries**:
  - `kafka-python`: Kafka producer and consumer.
  - `torch` and `timm`: For machine learning inference.
  - `Pillow`: For image processing.
  - `base64`: For image encoding/decoding.
  - `couchdb`: For interacting with the CouchDB database.
  
### Machine Learning Model

For image classification, we use a pre-trained **ResNet-20** model from **PyTorch Hub**, specifically designed for the **CIFAR-10** dataset. The model is loaded using the following command:

```python
model = torch.hub.load('chenyaofo/pytorch-cifar-models', 'cifar10_resnet20', pretrained=True)
```

**ResNet-20** is a well-optimized model for CIFAR-10 and provides a good balance between computational efficiency and accuracy for small image sizes like 32x32 pixels. It utilizes residual connections to mitigate the vanishing gradient problem commonly found in deep networks.

### Why ResNet-20?

- **Tailored for CIFAR-10**: This model is specifically designed and trained for the CIFAR-10 dataset, making it highly suitable for classifying its small image sizes.
- **Computational Efficiency**: ResNet-20 offers a good balance between accuracy and computational speed.
- **Residual Connections**: These connections allow the model to train deeper networks effectively without running into the vanishing gradient problem.

Using this pre-trained model allows us to achieve reasonable classification performance without needing extensive training on the CIFAR-10 dataset.

## Setup Instructions

### Step 1: Setup VMs using Ansible

Use the provided `playbook_master.yaml` to automate the creation of VMs on Chameleon Cloud (or any supported cloud service).

Ensure that your Ansible environment is configured with access to the cloud provider.

Run the Ansible playbook to create the necessary VMs and install required packages (Docker, Python, etc.):

```bash
ansible-playbook playbook_master.yaml
```

The playbook will:
- Create VMs.
- Install Docker and Docker Compose.
- Configure the environment for running the Docker services.

### Step 2: Build and Run Docker Services on VMs

Once the VMs are set up, SSH into the VMs and run the Docker services using Docker Compose.

SSH into the VM where Docker will be running:

```bash
ssh user@<vm_ip_address>
```

Navigate to the directory where the `docker-compose.yaml` file is located and run:

```bash
docker-compose up --build
```

This command will:
- Build Docker images for the producer, inference, and consumer services.
- Start the Kafka, Zookeeper, producer, and inference containers.

### Step 3: Running the Producer and Inference Services

Once the Docker containers are running:

#### Run the Producer

This sends images to Kafka for inference.

```bash
docker exec -it <producer_container_name> python producer.py
```

The producer sends images from the CIFAR-10 dataset to Kafka and receives inference results.

#### Run the Inference Service

This performs the image classification using the pre-trained model and sends the results to Kafka.

```bash
docker exec -it <inference_container_name> python inference.py
```

The inference service listens to the Kafka topic for incoming images, performs inference using the ResNet model, and sends the results back to Kafka.

#### Run the Consumer

The consumer processes the inference results and computes the end-to-end latency.

```bash
docker exec -it <consumer_container_name> python consumer.py
```

### Step 4: Analyze the Latency Results

The latency results for each image inference will be saved in a file `latency_results.txt` and visualized as a histogram.

Once all the messages are processed, the `producer.py` script will generate a latency histogram and save it as `latency_histogram.png`:

```bash
python producer.py
```

This histogram shows the distribution of end-to-end latency for the messages.

## Files Description

- `producer.py`: Sends images to Kafka and listens for inference results to compute latency.
- `inference.py`: Performs image inference using a pre-trained ResNet model and sends results to Kafka.
- `consumer.py`: Listens for inference results and processes them.
- `Dockerfile`: Defines the image setup for the producer, inference, and consumer services.
- `docker-compose.yaml`: Docker Compose configuration to run Kafka, Zookeeper, and the application services.
- `playbook_master.yaml`: Ansible playbook to automate VM and Docker setup.
- `requirements.txt`: Python dependencies.

## Dependencies

The following Python packages are required:

```bash
numpy
pandas
flask
kafka-python
torch
torchvision
requests
couchdb
matplotlib
```

Install these using:

```bash
pip install -r requirements.txt
```

## Results

After running the pipeline, the project will generate a file `latency_results.txt` with latency data for each image. A latency histogram will also be generated and saved as `latency_histogram.png`.
