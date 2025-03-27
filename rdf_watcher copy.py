# rdf_watcher.py
import os
import time
import hashlib
import logging
from fuseki.fuseki_sync import sync_with_fuseki
from update.update_pipeline import main as run_embedding_pipeline
from datetime import datetime

RDF_FILE = "./data/rdf.xml"
CHECK_INTERVAL = 5

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = f"logs/rdf_watch_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def watch_rdf_file():
    if not os.path.exists(RDF_FILE):
        logging.error(f"❌ {RDF_FILE} 파일이 존재하지 않습니다.")
        return

    last_hash = get_file_hash(RDF_FILE)
    logging.info("👀 RDF 파일 변경 감지 시작...")

    while True:
        time.sleep(CHECK_INTERVAL)
        current_hash = get_file_hash(RDF_FILE)
        if current_hash != last_hash:
            logging.info("🔄 RDF 파일 변경 감지됨!")
            updated = sync_with_fuseki()
            if updated:
                run_embedding_pipeline()
            last_hash = current_hash

if __name__ == "__main__":
    watch_rdf_file()
