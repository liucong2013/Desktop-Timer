import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PyQt6.QtGui import QAction, QCursor, QScreen, QGuiApplication
from pynput import keyboard, mouse
import time

class DesktopTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initCounters()
        self.initKeyboardListener()
        self.initMouseListener()
        self.edge_buffer = 20
        self.original_size = None
        self.original_stats_hidden_size = None
        self.stats_visible = False
        self.just_started = True  # 新增：标记程序是否刚启动

    def initUI(self):
        self.setWindowTitle('Desktop Timer')
        self.setGeometry(100, 100, 70, 25)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(1, 1, 1, 1)

        self.pause_button = QPushButton("⏸️", self)
        self.pause_button.setFixedSize(20, 20)
        self.pause_button.clicked.connect(self.togglePause)
        main_layout.addWidget(self.pause_button)

        self.timer_label = QLabel('00:00:00', self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(self.timer_label)

        self.stats_label = QLabel('', self)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.hide()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start(1000)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.addAction(QAction("关闭程序", self, triggered=self.close))
        self.toggle_seconds_action = QAction("隐藏秒数", self, triggered=self.toggleSeconds)
        self.addAction(self.toggle_seconds_action)
        self.toggle_topmost_action = QAction("取消置顶", self, triggered=self.toggleTopmost)
        self.addAction(self.toggle_topmost_action)

        self.show_seconds = True
        self.is_topmost = True
        self.is_paused = False
        self.is_minimized = False

        self.dragging = False
        self.offset = QPoint()

        self.original_size = QSize(91, 30)  # 设置一个固定的初始大小
        self.original_compact_size = QSize(91, 30)

        # 将窗口移动到右下角
        self.moveToBottomRight()
        
        QTimer.singleShot(1000, self.setJustStartedFalse)  # 1秒后将just_started设为False

    def setJustStartedFalse(self):
        self.just_started = False

    def initCounters(self):
        self.seconds = 0
        self.keyboard_count = 0
        self.mouse_count = 0
        self.idle_time = 0
        self.last_activity_time = time.time()

    def initKeyboardListener(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def initMouseListener(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def updateTimer(self):
        if not self.is_paused:
            self.seconds += 1
            self.checkIdleTime()
        hours, remainder = divmod(self.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if self.show_seconds:
            time_str = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        else:
            time_str = f'{hours:02d}:{minutes:02d}'
        self.timer_label.setText(time_str)

    def toggleSeconds(self):
        self.show_seconds = not self.show_seconds
        self.toggle_seconds_action.setText("显示秒数" if self.show_seconds else "隐藏秒数")
        self.updateTimer()

    def toggleTopmost(self):
        self.is_topmost = not self.is_topmost
        if self.is_topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.toggle_topmost_action.setText("取消置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.toggle_topmost_action.setText("始终置顶")
        self.show()

    def togglePause(self):
        self.is_paused = not self.is_paused
        self.pause_button.setText("▶️" if self.is_paused else "⏸️")

    def on_key_press(self, key):
        if not self.is_paused:
            self.keyboard_count += 1
            self.last_activity_time = time.time()

    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_paused and pressed:
            self.mouse_count += 1
            self.last_activity_time = time.time()

    def checkIdleTime(self):
        current_time = time.time()
        if current_time - self.last_activity_time > 20:
            self.idle_time += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.dragging:
                self.toggleStatsDisplay()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if not self.dragging:
                self.dragging = True
                self.drag_start_position = event.globalPosition().toPoint()
                self.window_start_position = self.pos()
            else:
                new_pos = self.window_start_position + event.globalPosition().toPoint() - self.drag_start_position
                screen = QApplication.screenAt(new_pos)
                if screen:
                    screen_geometry = screen.availableGeometry()
                    
                    if not self.just_started:  # 只有在不是刚启动时才检查边缘
                        edge = self.getTouchedEdge(screen_geometry, new_pos)
                        if edge and not self.is_minimized:
                            self.minimizeWindow(screen_geometry, edge)
                        elif not edge and self.is_minimized:
                            self.restoreWindow()
                    
                    new_pos.setX(max(screen_geometry.left(), min(new_pos.x(), screen_geometry.right() - self.width())))
                    new_pos.setY(max(screen_geometry.top(), min(new_pos.y(), screen_geometry.bottom() - self.height())))
                    self.move(new_pos)
        
        super().mouseMoveEvent(event)

    def getTouchedEdge(self, screen, pos):
        threshold = 20  # 增加阈值
        if pos.x() <= screen.left() + threshold:
            return 'left'
        elif pos.x() + self.width() >= screen.right() - threshold:
            return 'right'
        elif pos.y() <= screen.top() + threshold:
            return 'top'
        elif pos.y() + self.height() >= screen.bottom() - threshold:
            return 'bottom'
        return None

    def minimizeWindow(self, screen, edge):
        if not self.is_minimized:
            self.is_minimized = True
            self.original_size = self.size()
            self.original_pos = self.pos()
            if edge in ['left', 'right']:
                self.setGeometry(self.x(), self.y(), 5, 50)
            else:
                self.setGeometry(self.x(), self.y(), 50, 5)
            print(f"Window minimized to {edge}. New size: {self.size()}")  # 调试信息

    def restoreWindow(self):
        if self.is_minimized:
            self.is_minimized = False
            self.resize(self.original_size)
            self.move(self.original_pos)
            print(f"Window restored. New size: {self.size()}")  # 调试信息

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

    def toggleStatsDisplay(self):
        if not self.stats_visible:
            self.stats_visible = True
            idle_hours, idle_remainder = divmod(self.idle_time, 3600)
            idle_minutes, idle_seconds = divmod(idle_remainder, 60)
            stats = (f"键盘: {self.keyboard_count:6d}\n"
                     f"鼠标: {self.mouse_count:6d}\n"
                     f"空闲: {idle_hours:02d}:{idle_minutes:02d}:{idle_seconds:02d}")
            self.stats_label.setText(stats)
            
            self.original_compact_size = self.size()
            
            self.stats_label.setStyleSheet("font-size: 14px; padding: 5px;")
            
            self.centralWidget().layout().addWidget(self.stats_label)
            self.stats_label.show()
            
            self.adjustSize()
            print(f"显示统计信息 - 原始大小: {self.original_compact_size}, 新大小: {self.size()}")
        else:
            self.stats_visible = False
            self.stats_label.hide()
            
            self.centralWidget().layout().removeWidget(self.stats_label)
            
            self.resize(self.original_compact_size)
            print(f"隐藏统计信息 - 恢复到原始大小: {self.original_compact_size}")

        self.original_size = self.size()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.stats_visible and not self.is_minimized:
            self.original_compact_size = self.size()

    def moveToBottomRight(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        
        window_width = self.width()
        window_height = self.height()
        
        x = screen.width() - window_width - 10  # 10是与屏幕右边缘的间距
        y = screen.height() - window_height - 10  # 10是与屏幕底部的间距
        
        self.move(screen.left() + x, screen.top() + y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer = DesktopTimer()
    timer.show()
    sys.exit(app.exec())