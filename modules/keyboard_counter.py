from pynput import keyboard  # 导入pynput库中的keyboard模块，用于监听键盘事件
from PyQt6.QtCore import QObject, pyqtSignal  # 导入QObject和pyqtSignal用于信号机制

class KeyboardCounter(QObject):
    key_pressed = pyqtSignal()  # 定义一个信号，当键被按下时触发
    
    def __init__(self):
        super().__init__()  # 调用父类QObject的构造方法
        self.count = 0  # 初始化键盘敲击次数为0
        self.listener = keyboard.Listener(on_press=self.on_press)  # 创建一个键盘监听器，连接按下事件到on_press方法
        self.is_running = False  # 标记监听器是否正在运行，初始为未启动
    
    def on_press(self, key):
        self.count += 1  # 增加键盘敲击次数
        self.key_pressed.emit()  # 触发key_pressed信号
    
    def start(self):
        if not self.is_running:  # 如果监听器未启动
            self.listener.start()  # 启动监听器
            self.is_running = True  # 更新运行状态为启动
    
    def stop(self):
        if self.is_running:  # 如果监听器正在运行
            self.listener.stop()  # 停止监听器
            self.is_running = False  # 更新运行状态为未启动
    
    def get_count(self):
        return self.count  # 返回当前的键盘敲击次数