import subprocess
import sys
import threading
import time

def run_flask():
    subprocess.run([sys.executable, "app.py"])

def run_streamlit():
    time.sleep(2)  # give Flask a 2-sec head start
    subprocess.run(["streamlit", "run", "landing.py"])  
if __name__ == "__main__":
    t1 = threading.Thread(target=run_flask)
    t2 = threading.Thread(target=run_streamlit)

    t1.start()
    t2.start()

    t1.join()
    t2.join()