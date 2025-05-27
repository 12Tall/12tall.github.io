from MyProjectBase import MainWindowBase,dlg_hello

import wx  
class Hello(dlg_hello):
    def __init__(self, parent, name):
        """对话框初始化是可以接收额外的参数"""
        super().__init__(parent)
        self.lbl_name.SetLabelText(name)

class MainWindow(MainWindowBase):
    def __init__(self, parent):
        super().__init__(parent)

    def open_hello_dialog(self, event):
        """重写设计器中指定的事件处理函数"""
        dlg = Hello(self, self.txt_name.GetValue())
        dlg.ShowModal()

# 程序运行的基本流程
app = wx.App()
main_window = MainWindow(None)
main_window.Show()
app.MainLoop()
