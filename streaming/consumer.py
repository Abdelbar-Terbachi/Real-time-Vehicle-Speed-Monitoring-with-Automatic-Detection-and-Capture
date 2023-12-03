from kafka import KafkaConsumer

# Initialize Kafka consumer
consumer = KafkaConsumer("screenshot", bootstrap_servers="localhost:9092")


def process_screenshot(message):
    # Implement your logic for processing the received screenshot message
    # This could involve saving the image, analyzing it, etc.
    print(f"Received screenshot message: {message.value}")


if __name__ == "__main__":
    for message in consumer:
        process_screenshot(message)
