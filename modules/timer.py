from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt

class Timer(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用父类QLabel的构造方法
        self.hours = 0  # 初始化小时数
        self.minutes = 0  # 初始化分钟数
        self.seconds = 0  # 初始化秒数
        self.show_seconds = True  # 标记是否显示秒数，初始为显示
        self.is_paused = False  # 标记计时器是否暂停，初始为未暂停
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文字居中对齐
        self.update_display()  # 更新显示的时间文本
        
        self.timer = QTimer()  # 创建一个QTimer实例
        self.timer.timeout.connect(self.update_time)  # 连接定时器的超时信号到update_time方法
        self.timer.start(1000)  # 启动定时器，设置每1000毫秒（1秒）触发一次
    
    def update_time(self):
        if not self.is_paused:  # 如果计时器未暂停
            self.seconds += 1  # 增加秒数
            if self.seconds >= 60:  # 如果秒数达到60
                self.seconds = 0  # 秒数归零
                self.minutes += 1  # 分钟数增加
            if self.minutes >= 60:  # 如果分钟数达到60
                self.minutes = 0  # 分钟数归零
                self.hours += 1  # 小时数增加
            self.update_display()  # 更新显示的时间文本
    
    def update_display(self):
        if self.show_seconds:  # 如果需要显示秒数
            time_text = f"{self.hours}时:{self.minutes}分:{self.seconds}秒"  # 格式化时间字符串
        else:
            time_text = f"{self.hours}时:{self.minutes}分"  # 只显示小时和分钟
        self.setText(time_text)  # 设置标签的文本
    
    def hide_seconds(self):
        self.show_seconds = False  # 设置不显示秒数
        self.update_display()  # 更新显示的时间文本
    
    def show_seconds_display(self):
        self.show_seconds = True  # 设置显示秒数
        self.update_display()  # 更新显示的时间文本
    
    def start_timer(self):
        self.is_paused = False  # 设置计时器为启动状态
    
    def stop_timer(self):
        self.is_paused = True  # 设置计时器为暂停状态