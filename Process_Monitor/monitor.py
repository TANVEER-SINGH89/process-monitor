import psutil
from collections import deque

class ProcessMonitor:
    def __init__(self):
        self.cpu_history = deque(maxlen=60)
        self.mem_history = deque(maxlen=60)

    def get_processes(self):
        processes = []

        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                processes.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "cpu": p.info['cpu_percent'],
                    "memory": round(p.info['memory_info'].rss / (1024 * 1024), 1)
                })
            except:
                pass

        self.cpu_history.append(psutil.cpu_percent())
        self.mem_history.append(psutil.virtual_memory().percent)

        return processes

    def kill_process(self, pid):
        try:
            psutil.Process(pid).terminate()
            return True
        except:
            return False