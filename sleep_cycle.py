import os
import time
from datetime import datetime
import subprocess

while True:
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    daily_dir = f"./images/{date_str}"
    if not os.path.exists(daily_dir): #if doesn't exist (newday) create new
        os.makedirs(daily_dir)

    image_path = f"{daily_dir}/image_{timestamp}.jpg" #capture image
    os.system(f"raspistill -o {image_path}") #save image

    os.system("sync") #make sure file is saved before sleep

    print("Image captured, going to sleep")

    subprocess.run(["sudo", "rtcwake", "-m", "mem", "-s", "50"]) #sleep for 50 seconds

    time.sleep(2) #buffer to reboot
