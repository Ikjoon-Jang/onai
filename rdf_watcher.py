# rdf_watcher.py
import os
import time
import hashlib
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from fuseki.fuseki_sync import sync_with_fuseki
from update.update_pipeline import main as run_embedding_pipeline

# RDF_FILE = "./data/rdf.xml"
RDF_FILE = os.getenv("RDF_FILE")

# 로그 파일에 시분초 포함
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

class RDFChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_hash = self.get_file_hash()

    def get_file_hash(self):
        with open(RDF_FILE, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def on_modified(self, event):
        if event.src_path.endswith("rdf.xml"):

            time.sleep(0.5)  # 👉 파일 접근 전에 잠시 대기

            current_hash = self.get_file_hash()
            if current_hash != self.last_hash:
                logging.info("🔄 RDF 파일 변경 감지됨!")
                updated = sync_with_fuseki()
                if updated:
                    run_embedding_pipeline()
                self.last_hash = current_hash


def watch_rdf_file():
    if not os.path.exists(RDF_FILE):
        logging.error(f"❌ {RDF_FILE} 파일이 존재하지 않습니다.")
        return

    if not os.access(RDF_FILE, os.R_OK):
        logging.error(f"❌ RDF 파일을 읽을 수 있는 권한이 없습니다: {RDF_FILE}")
        return

    logging.info("👀 RDF 파일 변경 감지 시작...")
    event_handler = RDFChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path="./data", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("🛑 감시 프로세스를 수동 종료했습니다.")

    observer.join()


if __name__ == "__main__":
    watch_rdf_file()
