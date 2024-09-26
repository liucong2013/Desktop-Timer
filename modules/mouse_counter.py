from pynput import mouse
from PyQt6.QtCore import QObject, pyqtSignal

class MouseCounter(QObject):
    mouse_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.count = 0
        self.listener = mouse.Listener(on_click=self.on_click)
        self.is_running = False
    
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.count += 1
            self.mouse_clicked.emit()
    
    def start(self):
        if not self.is_running:
            self.listener.start()
            self.is_running = True
    
    def stop(self):
        if self.is_running:
            self.listener.stop()
            self.is_running = False
    
    def get_count(self):
        return self.count