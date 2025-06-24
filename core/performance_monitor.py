# New file: core/performance_monitor.py
import psutil
import os
import threading
import time

class PerformanceMonitor:
    def __init__(self, interval=10):
        self.interval = interval
        self.running = False
        self.thread = None
        
    def start(self):
        """Start monitoring in a background thread"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        process = psutil.Process(os.getpid())
        
        while self.running:
            # Get memory info
            mem_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            
            print(f"MONITOR: Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB, "
                  f"CPU: {cpu_percent:.1f}%")
                  
            # Log if memory usage is high
            if mem_info.rss > 500 * 1024 * 1024:  # If over 500MB
                print("MONITOR: WARNING - High memory usage detected!")
                
            time.sleep(self.interval)