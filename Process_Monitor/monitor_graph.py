import time
import psutil
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

_sys_anim = None
_proc_anim = None

# ================= SYSTEM GRAPH =================
def start_graph_monitor(cpu_history, mem_history):
    global _sys_anim

    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title("System Resource Monitor")

    ax.set_title("System CPU & Memory Usage")
    ax.set_xlabel("Time")
    ax.set_ylabel("Usage (%)")
    ax.set_ylim(0, 100)

    cpu_line, = ax.plot([], [], label="CPU %", linewidth=2, color="orange")
    mem_line, = ax.plot([], [], label="Memory %", linewidth=2, color="blue")

    ax.legend()
    ax.grid(True)

    def update(frame):
        x = list(range(len(cpu_history)))
        cpu_line.set_data(x, cpu_history)
        mem_line.set_data(x, mem_history)
        ax.set_xlim(0, max(60, len(cpu_history)))
        return cpu_line, mem_line

    _sys_anim = FuncAnimation(fig, update, interval=1000)
    plt.show(block=False)


# ================= PROCESS GRAPH =================
def start_process_graph(pid):
    global _proc_anim

    cpu_hist, mem_hist, time_hist = [], [], []
    start_time = time.time()

    try:
        proc = psutil.Process(pid)
        proc.cpu_percent(None)  # prime CPU
    except psutil.NoSuchProcess:
        return

    fig, ax1 = plt.subplots()
    fig.canvas.manager.set_window_title(f"Process Monitor (PID {pid})")

    ax1.set_title("Process CPU & Memory Usage")
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("CPU Usage (%)")
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Memory Usage (MB)")

    cpu_line, = ax1.plot([], [], label="CPU %", linewidth=2, color="orange")
    mem_line, = ax2.plot([], [], label="Memory MB", linewidth=2, color="blue")

    fig.legend()
    ax1.grid(True)

    def update(frame):
        try:
            cpu = max(0.0, proc.cpu_percent(None))
            mem = max(0.0, proc.memory_info().rss / (1024 * 1024))
        except psutil.NoSuchProcess:
            fig.suptitle("Process Ended", color="red")
            return cpu_line, mem_line

        elapsed = time.time() - start_time

        cpu_hist.append(cpu)
        mem_hist.append(mem)
        time_hist.append(elapsed)

        cpu_line.set_data(time_hist, cpu_hist)
        mem_line.set_data(time_hist, mem_hist)

        ax1.set_xlim(0, max(10, elapsed))
        ax2.set_ylim(0, max(mem_hist) + 50)

        return cpu_line, mem_line

    _proc_anim = FuncAnimation(fig, update, interval=1000)
    plt.show(block=False)