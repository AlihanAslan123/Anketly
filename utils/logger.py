import logging
from datetime import datetime
from pathlib import Path


# Logger ayarı
def log_start(job_name:str):
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("/logs")
    #log_dir.mkdir(parents=True, exist_ok=True)
    #log_file_name = f"/logs/{job_name}_{current_date}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            #logging.FileHandler(log_file_name,encoding="utf-8"),
            logging.StreamHandler() 
        ]
    )
 
def get_logger():
    return logging.getLogger("logging_utils")