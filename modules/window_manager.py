from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMenu  # 导入必要的PyQt6组件
from PyQt6.QtCore import Qt, QTimer, QPoint  # 导入必要的PyQt6核心类
from modules.timer import Timer  # 导入Timer模块
from modules.keyboard_counter import KeyboardCounter  # 导入KeyboardCounter模块
from modules.mouse_counter import MouseCounter  # 导入MouseCounter模块
from modules.idle_tracker import IdleTracker  # 导入IdleTracker模块
# from modules.edge_snap import EdgeSnap  # {{ edit_1: 移除 EdgeSnap 引用 }}

class WindowManager(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类QMainWindow的构造方法
        self.setWindowTitle("计时器程序")  # 设置窗口标题
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)  # 设置窗口标志，使窗口始终置顶并去除边框
        self.setGeometry(100, 100, 300, 100)  # 设置窗口的位置和大小（x, y, 宽, 高）
        
        self.timer = Timer(self)  # 创建Timer实例，并将当前窗口作为父对象
        self.keyboard_counter = KeyboardCounter()  # 创建KeyboardCounter实例
        self.mouse_counter = MouseCounter()  # 创建MouseCounter实例
        self.idle_tracker = IdleTracker(self.keyboard_counter, self.mouse_counter)  # 创建IdleTracker实例，传入键盘和鼠标计数器
        # self.edge_snap = EdgeSnap(self)  # {{ edit_2: 移除 EdgeSnap 的实例化 }}
        
        self.init_ui()  # 初始化用户界面
        self.init_context_menu()  # 初始化右键上下文菜单
        self.is_info_visible = False  # 标记信息显示状态，初始为隐藏
        
    def init_ui(self):
        central_widget = QWidget()  # 创建中心窗口部件
        layout = QVBoxLayout()  # 创建垂直布局管理器
        
        layout.addWidget(self.timer)  # 将计时器添加到布局中
        
        self.toggle_button = QPushButton("暂停")  # 创建一个按钮，初始标签为"暂停"
        self.toggle_button.clicked.connect(self.toggle_counters)  # 连接按钮点击事件到toggle_counters方法
        layout.addWidget(self.toggle_button)  # 将按钮添加到布局中
        
        central_widget.setLayout(layout)  # 设置中心部件的布局
        self.setCentralWidget(central_widget)  # 将中心部件设置为主窗口的中心部件
        
        # 连接计时器的左键点击事件到timer_clicked方法
        self.timer.mousePressEvent = self.timer_clicked

    def init_context_menu(self):
        self.context_menu = QMenu(self)  # 创建一个右键菜单
        
        # 添加"隐藏秒数"或"显示秒数"选项
        self.show_hide_seconds_action = self.context_menu.addAction("隐藏秒数")
        self.show_hide_seconds_action.triggered.connect(self.toggle_seconds_display)  # 连接触发事件到toggle_seconds_display方法
        
        # 添加"取消始终置顶"或"始终置顶"选项
        self.toggle_stay_on_top_action = self.context_menu.addAction("取消始终置顶")
        self.toggle_stay_on_top_action.triggered.connect(self.toggle_stay_on_top)  # 连接触发事件到toggle_stay_on_top方法
        
        self.context_menu.addSeparator()  # 添加分隔线
        self.context_menu.addAction("关闭程序", self.close)  # 添加"关闭程序"选项，并连接到关闭窗口的方法
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:  # 如果鼠标右键被点击
            self.context_menu.exec(QCursor.pos())  # 在当前鼠标位置显示右键菜单
    
    def toggle_counters(self):
        if self.timer.is_paused:  # 如果计时器当前是暂停状态
            self.timer.start_timer()  # 启动计时器
            self.keyboard_counter.start()  # 启动键盘计数器
            self.mouse_counter.start()  # 启动鼠标计数器
            self.idle_tracker.start()  # 启动空闲时间跟踪器
            self.toggle_button.setText("暂停")  # 将按钮文本设置为"暂停"
        else:
            self.timer.stop_timer()  # 暂停计时器
            self.keyboard_counter.stop()  # 暂停键盘计数器
            self.mouse_counter.stop()  # 暂停鼠标计数器
            self.idle_tracker.stop()  # 暂停空闲时间跟踪器
            self.toggle_button.setText("启动")  # 将按钮文本设置为"启动"
    
    def toggle_seconds_display(self):
        if self.timer.show_seconds:  # 如果当前显示秒数
            self.timer.hide_seconds()  # 隐藏秒数
            self.show_hide_seconds_action.setText("显示秒数")  # 将菜单选项改为"显示秒数"
        else:
            self.timer.show_seconds_display()  # 显示秒数
            self.show_hide_seconds_action.setText("隐藏秒数")  # 将菜单选项改为"隐藏秒数"
    
    def toggle_stay_on_top(self):
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:  # 如果当前窗口是始终置顶
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)  # 取消始终置顶标志
            self.toggle_stay_on_top_action.setText("始终置顶")  # 将菜单选项改为"始终置顶"
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)  # 添加始终置顶标志
            self.toggle_stay_on_top_action.setText("取消始终置顶")  # 将菜单选项改为"取消始终置顶"
        self.show()  # 重新显示窗口以应用更改
    
    def timer_clicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:  # 如果鼠标左键被点击
            if not self.is_info_visible:  # 如果信息当前未显示
                # 创建显示统计信息的字符串
                info = (
                    f"鼠标点击次数: {self.mouse_counter.get_count()}\n"
                    f"键盘敲击次数: {self.keyboard_counter.get_count()}\n"
                    f"空闲时间: {self.idle_tracker.get_idle_time_formatted()}"
                )
                self.info_label = QLabel(info, self)  # 创建一个标签来显示信息
                self.info_label.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 150);  /* 设置背景颜色为半透明黑色 */
                    color: white;  /* 设置文字颜色为白色 */
                    padding: 10px;  /* 设置内边距 */
                    border-radius: 5px;  /* 设置圆角半径 */
                """)
                self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文字居中
                self.info_label.adjustSize()  # 自动调整标签大小以适应内容
                self.info_label.move(
                    self.timer.x(),  # 将标签移动到计时器的x位置
                    self.timer.y() + self.timer.height() + 10  # 将标签移动到计时器下方10像素
                )
                self.info_label.show()  # 显示信息标签
                self.is_info_visible = True  # 更新信息显示状态
            else:
                self.info_label.hide()  # 隐藏信息标签
                self.is_info_visible = False  # 更新信息显示状态