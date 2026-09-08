import csv
import json
import random

from datetime import datetime, timedelta
from pathlib import Path

# --- CONFIGURATION ---
OUTPUT_FORMAT = "text"  # Options: 'text' (Standard Apache/Nginx), 'json', or 'csv'
NUM_LOGS = 1000  # Number of log entries to generate

# --- SEED DATA FOR SIMULATION ---
IP_POOL = [f"192.168.1.{random.randint(10, 250)}" for _ in range(20)] + [
    "10.0.0.5", "10.0.0.12", "45.33.22.11", "185.220.101.5" ]

METHODS = ["GET", "POST", "PUT", "DELETE"]

RESOURCES = [   # Things the simulated server is "hosting", "access weight"
    ("/index.html", 0.4),
    ("/about.html", 0.1),
    ("/products", 0.15),
    ("/login", 0.1),
    ("/api/v1/data", 0.1),
    ("/wp-admin/phpmyadmin", 0.02),  # Malicious scan target
    ("/admin/config", 0.03), ]        # Malicious scan target

N_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://google.com)" ]

AN_USER_AGENTS = [  #Any abnormal agents go here
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://google.com)",
    "sqlmap/1.8.2#stable (https://sqlmap.org)" ] # Attack tool signature\

STATUS_CODES = [200, 200, 200, 200, 201, 301, 404, 404, 500, 403]

# --- HELPER FUNCTIONS ---
def get_weighted_choice(choices):
    elements, weights = zip(*choices)
    return random.choices(elements, weights=weights)[0]

def generate_log_line(timestamp, is_anomolous:bool = False):
    ip = random.choice(IP_POOL)
    method = random.choice(METHODS)
    resource = get_weighted_choice(RESOURCES)
    
    # Force specific behavior based on resource to make data realistic
    if "admin" in resource: #is anomolous if admin access
        status = random.choice([403, 404, 200])  # Unauthorized/Not Found

        if not is_anomolous:
            user_agent = N_USER_AGENTS[3] if random.random() > 0.5 else random.choice(N_USER_AGENTS)
        else: user_agent = AN_USER_AGENTS[4] if random.random() > 0.5 else random.choice(AN_USER_AGENTS)
    else:
        status = random.choice(STATUS_CODES)

        if not is_anomolous: user_agent = random.choice(N_USER_AGENTS[:3])
        else: user_agent = random.choice(AN_USER_AGENTS[:4])
        
    protocol = "HTTP/1.1"
    
    # Bytes sent configuration
    if status == 200: bytes_sent = random.randint(230, 4500)
    else: bytes_sent = random.randint(20, 160)

    # Format timestamp to Apache Combined Log Format: [dd/MMM/yyyy:HH:mm:ss +0000]
    time_str = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")
    
    return {
        "ip": ip,
        "timestamp": time_str,
        "method": method,
        "resource": resource,
        "protocol": protocol,
        "status": status,
        "bytes": bytes_sent,
        "referrer": "-",
        "user_agent": user_agent }

def GenerateLogName(iteration:int, is_anomolous: bool, is_training_data: bool) -> Path:
    log_path:Path = (Path.cwd() / "logs/")
    if is_training_data: 
        log_path = log_path / "training_data/"
        if is_anomolous: 
            log_name = f"SLog_Anomolous_{iteration}.{'txt' if OUTPUT_FORMAT == 'text' else OUTPUT_FORMAT}" 
            log_path =log_path / log_name
        else: 
            log_name = f"SLog_Normal_{iteration}.{'txt' if OUTPUT_FORMAT == 'text' else OUTPUT_FORMAT}"
            log_path =log_path / log_name
    else:
        log_path = log_path / "test_data/"
        if is_anomolous: 
            log_name = f"SLog_Anomolous_{iteration}.{'txt' if OUTPUT_FORMAT == 'text' else OUTPUT_FORMAT}"
            log_path =log_path / log_name
        else: 
            log_name = f"SLog_Normal_{iteration}.{'txt' if OUTPUT_FORMAT == 'text' else OUTPUT_FORMAT}"
            log_path =log_path / log_name

    return log_path


# --- GENERATION LOOP ---
def main(iterations:int, is_anomolous:bool = False, is_training_data:bool = True):
    for i in range(iterations):
        log = GenerateLogName(i, is_anomolous, is_training_data)
        start_time = datetime.utcnow() - timedelta(days=1)
        logs = []

        for i in range(NUM_LOGS):
            # Progressively increment time so the logs are in chronological order
            start_time += timedelta(seconds=random.randint(1, 60))
            logs.append(generate_log_line(start_time, is_anomolous))

        # --- WRITING TO FILE ---
        if OUTPUT_FORMAT == "text":
            with open(log, "w") as f:
                for log in logs:
                    f.write(f'{log["ip"]} - - [{log["timestamp"]}] "{log["method"]} {log["resource"]} {log["protocol"]}" {log["status"]} {log["bytes"]} "{log["referrer"]}" "{log["user_agent"]}"\n')

        elif OUTPUT_FORMAT == "json": 
            with open(log, "w") as f: json.dump(logs, f, indent=4)

        elif OUTPUT_FORMAT == "csv":
            with open(log, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)

if __name__ == "__main__": main(4, True, False)