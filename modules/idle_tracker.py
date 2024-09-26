from PyQt6.QtCore import QTimer

class IdleTracker:
    def __init__(self, keyboard_counter, mouse_counter):
        self.keyboard_counter = keyboard_counter
        self.mouse_counter = mouse_counter
        self.idle_time = 0
        self.idle_threshold = 20  # 秒
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_idle)
        self.timer.start(1000)
        self.is_idle = False
    
    def check_idle(self):
        if self.keyboard_counter.get_count() == 0 and self.mouse_counter.get_count() == 0:
            self.idle_time += 1
            if self.idle_time >= self.idle_threshold:
                self.is_idle = True
        else:
            self.idle_time = 0
            self.is_idle = False
    
    def start(self):
        self.timer.start(1000)
    
    def stop(self):
        self.timer.stop()

    def get_idle_time_formatted(self):
        hours = self.idle_time // 3600
        minutes = (self.idle_time % 3600) // 60
        seconds = self.idle_time % 60
        return f"{hours}时:{minutes}分:{seconds}秒"