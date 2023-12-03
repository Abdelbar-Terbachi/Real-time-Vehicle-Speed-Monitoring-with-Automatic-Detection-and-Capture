from kafka import KafkaProducer
import time
import os

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers="localhost:9092")

# Path to the folder containing screenshots
screenshot_folder = "screenshots"


def send_screenshot(image_path):
    try:
        with open(image_path, "rb") as f:
            producer.send("screenshot", value=f.read())
        print(f"Screenshot '{image_path}' sent successfully.")
        os.remove(image_path)  # Remove the image after sending to Kafka
    except Exception as e:
        print(f"Error sending screenshot: {e}")


def check_for_new_screenshots():
    while True:
        # Check for new screenshots every second
        time.sleep(1)

        # List all files in the screenshot folder
        screenshots = [
            f
            for f in os.listdir(screenshot_folder)
            if os.path.isfile(os.path.join(screenshot_folder, f))
        ]

        for screenshot in screenshots:
            image_path = os.path.join(screenshot_folder, screenshot)
            send_screenshot(image_path)


if __name__ == "__main__":
    check_for_new_screenshots()
