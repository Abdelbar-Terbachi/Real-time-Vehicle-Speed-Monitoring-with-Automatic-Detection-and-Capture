import cv2
import dlib
import time
import threading
import math
import os


# Chargement du classificateur en cascade pour la détection des voitures
car_cascade = cv2.CascadeClassifier("myhaar.xml")

# Chargement de la vidéo d'entrée
video = cv2.VideoCapture("cars.mp4")

# Paramètres de la vidéo
width = 1280
height = 720
fps = 18

# Dossier pour sauvegarder les captures d'écran des voitures
screenshot_folder = "screenshots"

# Assurez-vous que le dossier des captures d'écran existe
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)


# Fonction pour estimer la vitesse des voitures
def estimate_speed(location1, location2):
    d_pixels = math.sqrt(
        math.pow(location2[0] - location1[0], 2)
        + math.pow(location2[1] - location1[1], 2)
    )
    ppm = 8.8
    d_meters = d_pixels / ppm
    speed = d_meters * fps * 3.6
    return speed


# Fonction pour capturer et sauvegarder une capture d'écran d'une voiture
def capture_and_save_screenshot(car_id, speed, frame, car_rect):
    if speed > 60:
        x, y, w, h = car_rect
        car_roi = frame[y : y + h, x : x + w]

        screenshot_filename = (
            f"{screenshot_folder}/car_{car_id}_speed_{int(speed)}kmh.jpg"
        )
        cv2.imwrite(screenshot_filename, car_roi)
        print(f"Screenshot saved: {screenshot_filename}")


def track_multiple_objects():
    # Couleur du rectangle pour les voitures
    rectangle_color = (0, 255, 0)
    frame_counter = 0
    current_car_id = 0

    # Dictionnaires pour suivre les voitures
    car_tracker = {}
    car_location1 = {}
    car_location2 = {}
    speed = [None] * 1000

    # Écrire la sortie dans un fichier vidéo
    out = cv2.VideoWriter(
        "outpy.avi", cv2.VideoWriter_fourcc("M", "J", "P", "G"), 10, (width, height)
    )

    while True:
        start_time = time.time()
        rc, image = video.read()
        if type(image) == type(None):
            break

        image = cv2.resize(image, (width, height))
        result_image = image.copy()

        frame_counter += 1

        car_id_to_delete = []

        for car_id in car_tracker.keys():
            tracking_quality = car_tracker[car_id].update(image)

            if tracking_quality < 7:
                car_id_to_delete.append(car_id)

        for car_id in car_id_to_delete:
            print(f"Removing carID {car_id} from list of trackers.")
            print(f"Removing carID {car_id} previous location.")
            print(f"Removing carID {car_id} current location.")
            car_tracker.pop(car_id, None)
            car_location1.pop(car_id, None)
            car_location2.pop(car_id, None)

        if not (frame_counter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = car_cascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for _x, _y, _w, _h in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                match_car_id = None

                for car_id in car_tracker.keys():
                    tracked_position = car_tracker[car_id].get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if (
                        (t_x <= x_bar <= (t_x + t_w))
                        and (t_y <= y_bar <= (t_y + t_h))
                        and (x <= t_x_bar <= (x + w))
                        and (y <= t_y_bar <= (y + h))
                    ):
                        match_car_id = car_id

                if match_car_id is None:
                    print(f"Creating new tracker {current_car_id}")

                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                    car_tracker[current_car_id] = tracker
                    car_location1[current_car_id] = [x, y, w, h]

                    current_car_id += 1

        for car_id in car_tracker.keys():
            tracked_position = car_tracker[car_id].get_position()

            t_x = int(tracked_position.left())
            t_y = int(tracked_position.top())
            t_w = int(tracked_position.width())
            t_h = int(tracked_position.height())

            cv2.rectangle(
                result_image, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangle_color, 4
            )

            # Estimation de la vitesse
            car_location2[car_id] = [t_x, t_y, t_w, t_h]

        end_time = time.time()

        if not (end_time == start_time):
            fps = 1.0 / (end_time - start_time)

        for i in car_location1.keys():
            if frame_counter % 1 == 0:
                [x1, y1, w1, h1] = car_location1[i]
                [x2, y2, w2, h2] = car_location2[i]

                car_location1[i] = [x2, y2, w2, h2]

                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] is None or speed[i] == 0) and 275 <= y1 <= 285:
                        speed[i] = estimate_speed([x1, y1, w1, h1], [x2, y2, w2, h2])
                        capture_and_save_screenshot(
                            i, speed[i], result_image, car_location2[i]
                        )

                    if speed[i] is not None and y1 >= 180:
                        cv2.putText(
                            result_image,
                            f"{int(speed[i])} km/hr",
                            (int(x1 + w1 / 2), int(y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            (255, 255, 255),
                            2,
                        )

        cv2.imshow("result", result_image)

        if cv2.waitKey(33) == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    track_multiple_objects()
