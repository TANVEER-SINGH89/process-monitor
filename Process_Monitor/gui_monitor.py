import tkinter as tk
from tkinter import ttk, messagebox
from monitor import ProcessMonitor
from monitor_graph import start_graph_monitor, start_process_graph

REFRESH_TIME = 3000  # heavy refresh (psutil)

class ProcessMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("750x450")

        self.monitor = ProcessMonitor()
        self.cached_processes = []   # 🔑 cache for fast search

        self.create_widgets()
        self.update_data()

    # ================= UI =================
    def create_widgets(self):
        # ---------- SEARCH BAR ----------
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Search:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_view())

        # ---------- TABLE ----------
        self.tree = ttk.Treeview(
            self.root,
            columns=("PID", "Name", "CPU (%)", "Memory (MB)"),
            show="headings"
        )

        for col in ("PID", "Name", "CPU (%)", "Memory (MB)"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)

        tk.Button(
            btn_frame,
            text="Show System Graph",
            command=self.show_system_graph
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Show Selected Process Graph",
            command=self.show_process_graph
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Kill Selected Process",
            command=self.kill_selected_process,
            bg="#c0392b",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

    # ================= DATA LOOP =================
    def update_data(self):
        # heavy operation every 3 seconds
        self.cached_processes = self.monitor.get_processes()
        self.refresh_view()

        self.root.after(REFRESH_TIME, self.update_data)

    # ================= FAST SEARCH =================
    def refresh_view(self):
        self.tree.delete(*self.tree.get_children())

        keyword = self.search_var.get().lower()

        for p in self.cached_processes:
            if keyword:
                if keyword not in p["name"].lower() and keyword not in str(p["pid"]):
                    continue

            self.tree.insert(
                "", tk.END,
                values=(p["pid"], p["name"], p["cpu"], p["memory"])
            )

    # ================= ACTIONS =================
    def show_system_graph(self):
        start_graph_monitor(
            self.monitor.cpu_history,
            self.monitor.mem_history
        )

    def show_process_graph(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a process first")
            return

        pid = int(self.tree.item(selected[0])["values"][0])
        start_process_graph(pid)

    def kill_selected_process(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a process first")
            return

        pid = int(self.tree.item(selected[0])["values"][0])

        confirm = messagebox.askyesno(
            "Confirm Kill",
            f"Are you sure you want to terminate process {pid}?"
        )

        if not confirm:
            return

        success = self.monitor.kill_process(pid)

        if success:
            messagebox.showinfo("Success", f"Process {pid} terminated")
            self.update_data()
        else:
            messagebox.showerror("Error", "Failed to terminate process")

# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessMonitorGUI(root)
    root.mainloop()