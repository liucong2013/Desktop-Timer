import sys
from PyQt6.QtWidgets import QApplication
from modules.window_manager import WindowManager
# from modules.edge_snap import EdgeSnap  // {{ edit_1: 移除 EdgeSnap 引用 }}
from modules.timer import Timer
from modules.keyboard_counter import KeyboardCounter
from modules.mouse_counter import MouseCounter
from modules.idle_tracker import IdleTracker

def main():
    app = QApplication(sys.argv)  # 创建QApplication实例，传入命令行参数
    
    window_manager = WindowManager()  # 创建主窗口管理器实例
    # edge_snap = EdgeSnap(window_manager)  # {{ edit_2: 移除 EdgeSnap 的实例化 }}
    timer = Timer(window_manager)  # 创建计时器实例，并将窗口管理器传递给它
    keyboard_counter = KeyboardCounter()  # 创建键盘计数器实例
    mouse_counter = MouseCounter()  # 创建鼠标计数器实例
    idle_tracker = IdleTracker(keyboard_counter, mouse_counter)  # 创建空闲时间跟踪器实例，传入键盘和鼠标计数器
    
    window_manager.show()  # 显示主窗口
    
    sys.exit(app.exec())  # 启动应用程序的主循环，并在退出时关闭程序

if __name__ == "__main__":
    main()  # 如果此文件作为主程序执行，则调用main函数