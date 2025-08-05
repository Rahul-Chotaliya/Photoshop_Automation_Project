# utils.py

import os
import datetime

def setup_logging(log_dir="./logs"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    return log_file

def log_error(error_message, log_path="./logs/error_log.txt"):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {error_message}\n")

def create_output_dirs(base_output="./output/", thumbnail_output="./output/thumbnails/"):
    os.makedirs(base_output, exist_ok=True)
    os.makedirs(thumbnail_output, exist_ok=True)

def is_back_location(location):
    back_keywords = ["BACK", "FULL-BACK"]
    return any(keyword.lower() in location.lower() for keyword in back_keywords)

def is_front_location(location):
    front_keywords = ["FRONT", "FULL-FRONT"]
    return any(keyword.lower() in location.lower() for keyword in front_keywords)



