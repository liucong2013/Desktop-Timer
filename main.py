import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
from PyQt6.QtGui import QIcon, QAction
from pynput import keyboard, mouse

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Timer")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧布局（用于暂停/启动按钮）
        left_layout = QVBoxLayout()
        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon("pause.png"))  # 请确保有一个 pause.png 文件
        self.pause_button.setFixedSize(30, 30)
        self.pause_button.clicked.connect(self.toggle_pause)
        left_layout.addWidget(self.pause_button)
        left_layout.addStretch()
        
        # 创建右侧布局（用于计时器和统计信息）
        right_layout = QVBoxLayout()
        
        # 创建计时器标签
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.timer_label)
        
        # 创建统计信息标签
        self.stats_label = QLabel("键盘: 0 | 鼠标: 0 | 空闲: 00:00:00")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.hide()
        right_layout.addWidget(self.stats_label)
        
        # 将左侧和右侧布局添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        # 设置计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 每秒更新一次
        
        self.seconds = 0
        self.show_seconds = True
        self.always_on_top = True
        self.is_minimized = False
        self.is_paused = False
        
        # 键盘和鼠标计数器
        self.keyboard_count = 0
        self.mouse_count = 0
        self.idle_seconds = 0
        self.last_activity_time = 0
        
        # 创建右键菜单
        self.create_context_menu()
        
        # 设置窗口大小和位置
        self.normal_size = QRect(100, 100, 200, 100)
        self.setGeometry(self.normal_size)
        
        # 设置键盘和鼠标监听器
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        # 加载设置
        self.load_settings()
        
    def update_timer(self):
        if not self.is_paused:
            self.seconds += 1
            self.update_idle_time()
        hours, remainder = divmod(self.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if self.show_seconds:
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}")
        
        # 更新统计信息
        idle_hours, idle_remainder = divmod(self.idle_seconds, 3600)
        idle_minutes, idle_seconds = divmod(idle_remainder, 60)
        self.stats_label.setText(f"键盘: {self.keyboard_count} | 鼠标: {self.mouse_count} | 空闲: {idle_hours:02d}:{idle_minutes:02d}:{idle_seconds:02d}")

    def create_context_menu(self):
        self.context_menu = QMenu(self)
        
        # 关闭程序选项
        close_action = QAction("关闭程序", self)
        close_action.triggered.connect(self.close)
        self.context_menu.addAction(close_action)
        
        # 显示/隐藏秒数选项
        self.toggle_seconds_action = QAction("隐藏秒数", self)
        self.toggle_seconds_action.triggered.connect(self.toggle_seconds)
        self.context_menu.addAction(self.toggle_seconds_action)
        
        # 切换始终置顶选项
        self.toggle_on_top_action = QAction("取消置顶", self)
        self.toggle_on_top_action.triggered.connect(self.toggle_always_on_top)
        self.context_menu.addAction(self.toggle_on_top_action)

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def toggle_seconds(self):
        self.show_seconds = not self.show_seconds
        self.toggle_seconds_action.setText("显示秒数" if self.show_seconds else "隐藏秒数")
        self.update_timer()
        self.save_settings()

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.toggle_on_top_action.setText("取消置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.toggle_on_top_action.setText("始终置顶")
        self.show()  # 需要重新显示窗口以应用更改
        self.save_settings()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            if not self.stats_label.isVisible():
                self.stats_label.show()
            else:
                self.stats_label.hide()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.check_edge_proximity()
            event.accept()

    def check_edge_proximity(self):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.geometry()
        
        # 检查是否靠近屏幕边缘
        if (window_rect.left() <= 10 or 
            window_rect.right() >= screen.width() - 10 or 
            window_rect.top() <= 10 or 
            window_rect.bottom() >= screen.height() - 10):
            if not self.is_minimized:
                self.minimize_window()
        else:
            if self.is_minimized:
                self.restore_window()

    def minimize_window(self):
        self.normal_size = self.geometry()
        self.setFixedSize(10, 100)
        self.is_minimized = True
        self.pause_button.hide()

    def restore_window(self):
        self.setGeometry(self.normal_size)
        self.is_minimized = False
        self.pause_button.show()

    def on_key_press(self, key):
        if not self.is_paused:
            self.keyboard_count += 1
            self.last_activity_time = self.seconds

    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_paused and pressed:
            self.mouse_count += 1
            self.last_activity_time = self.seconds

    def update_idle_time(self):
        if self.seconds - self.last_activity_time >= 20:
            self.idle_seconds += 1

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.setIcon(QIcon("play.png"))  # 请确保有一个 play.png 文件
        else:
            self.pause_button.setIcon(QIcon("pause.png"))

    def save_settings(self):
        settings = {
            "show_seconds": self.show_seconds,
            "always_on_top": self.always_on_top,
            "window_position": [self.pos().x(), self.pos().y()],
            "window_size": [self.width(), self.height()],
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            self.show_seconds = settings.get("show_seconds", True)
            self.always_on_top = settings.get("always_on_top", True)
            position = settings.get("window_position", [100, 100])
            size = settings.get("window_size", [200, 100])
            self.setGeometry(QRect(QPoint(position[0], position[1]), QPoint(position[0] + size[0], position[1] + size[1])))
            self.toggle_seconds_action.setText("显示秒数" if not self.show_seconds else "隐藏秒数")
            self.toggle_on_top_action.setText("取消置顶" if self.always_on_top else "始终置顶")
            if not self.always_on_top:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()