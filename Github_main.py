import cv2
import time
import os
import pyrebase
import subprocess







command2 = f"sudo ip route del default via 192.168.1.1 dev eth0 src 192.168.1.2 metric 202"
command3 = f"sudo ip route del 192.168.1.0/24 dev eth0 proto dhcp scope link src 192.168.1.2 metric 202" 
command4 = f"sudo ip route add default via 192.168.1.1 dev eth0 src 192.168.1.2 metric 404"
command5 = f"sudo ip route add 192.168.1.1 dev eth0 src 192.168.1.2 metric 404"

try:
    subprocess.run(command2, shell=True, check=True)
    print(f"default route del success")
except subprocess.CalledProcessError as e:
    print(f"error in default route del")

try:
    subprocess.run(command3, shell=True, check=True)
    print(f"route del success")
except subprocess.CalledProcessError as e:
    print(f"error in route del")

try:
    subprocess.run(command4, shell=True, check=True)
    print(f"default route re add success")
except subprocess.CalledProcessError as e:
    print(f"error in default route re add")

try:
    subprocess.run(command5, shell=True, check=True)
    print(f"default route re add success")
except subprocess.CalledProcessError as e:
    print(f"error in default route re add")

# Firebase configuration
config = {   
    "apiKey": "AIzaSyAtWfvj6s2FxLRGSpVBCql2K6EbeLtoVvo",
   "authDomain": "raspberrypi-camera-uploads.firebaseapp.com",
   "databaseURL": "https://raspberrypi-camera-uploads-default-rtdb.firebaseio.com",
   "projectId": "raspberrypi-camera-uploads",
   "storageBucket": "raspberrypi-camera-uploads.appspot.com",
   "serviceAccount": "raspberrypi-camera-uploads-firebase-key.json",
    }

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Assuming your file is named "IPList.txt"
# file_path = "/home/habib/Desktop/IPList.txt"

# Function to fetch IP addresses from Firebase
def fetch_ip_addresses():
    ip_addresses = db.child("pi_E305654/ip_addresses").get().val()
    camera_list = []
    if ip_addresses:
        for ip_data in ip_addresses:
            ip = ip_data.get("ip")
            port = ip_data.get("port")
            username = ip_data.get("username")
            password = ip_data.get("password")
            camera_url = f"rtsp://{username}:{password}@{ip}:{port}/profile1/media.smp"
            command = f"sudo ip route add {ip}/32 dev eth0"
        try:
            subprocess.run(command, shell=True , check=True)
            print(f"route added for ip :{ip}" )
        except subprocess.CalledProcessError as e :
            print(f"error in route added for ip :{ip} jgygv" )
            camera_list.append(camera_url)
    return camera_list

# Main code
camera_list = fetch_ip_addresses()

print(camera_list)



# Create VideoCapture object outside the loop
cap = cv2.VideoCapture()

try:
    while True:
        for camera_url in camera_list:
            # Set the new camera URL
            cap.open(camera_url)

            # Check if the camera is opened successfully
            if not cap.isOpened():
                print(f"Error: Could not open camera at {camera_url}")
                continue

            # Read a frame from the camera
            ret, frame = cap.read()

            # Check if the frame is read successfully
            if not ret:
                print(f"Error: Could not read frame from camera at {camera_url}")
                continue

            # Specify the folder location
            folder_path = "/home/habib/Desktop/CameraOutput"

            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Create the filename as before
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"captured_image@_{timestamp}_{camera_url.replace(':', '_').replace('/', '_')}.jpg"

            # Combine folder path and filename
            full_path = os.path.join(folder_path, filename)

            # Save the file
            cv2.imwrite(full_path, frame)
            # Save the captured frame with a unique filename
            # filename = f"captured_image_{camera_url.replace(':', '_').replace('/', '_')}.jpg"
            # cv2.imwrite(filename, frame)

            print(f"Image captured from camera at {camera_url} and saved as {filename}")

            firebase_storage = pyrebase.initialize_app(config)
            storage = firebase_storage.storage()
            storage_ref = storage.child("/")

            local_file_path = f"/home/habib/Desktop/CameraOutput/{filename}"

            firebase_storage_path = filename

            storage_ref.child(firebase_storage_path).put(local_file_path)
            print("File uploaded successfully")
            os.remove(full_path)
        # Wait for one minute before capturing images again
        time.sleep(300)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()
