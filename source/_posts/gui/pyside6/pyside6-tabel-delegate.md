---
title: pyside6-tabel-delegate
date: 2024-05-23 14:35:15
tags: [python, qt, delegate]
categories: [开发]  
---

在Qt 的TableView 中添加其他`Widget`。     

<!--more-->   

效果图：  
![win.jpg](win.jpg)

代码：  

```python  
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QStyledItemDelegate,
    QStyleOptionButton,
    QStyle
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QEvent, Qt


# 创建组件委托
class MyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        """
        绘制组件，主要是依据index 中的行列信息绘制元素
        """
        if index.column() in (0,):              
            # 并没有专门的：QStyleOptionTextEdit
            button_option = QStyleOptionButton()
            button_option.rect = option.rect # 矩形
            button_option.text = f"Click ({index.row()},{index.column()})" 
            button_option.state = QStyle.State_Enabled
            # 绘制元素的样式
            QApplication.style().drawControl(QStyle.CE_PushButton, button_option, painter)
        elif index.column() in (1,):
            checkbox_option = QStyleOptionButton()
            checkbox_option.rect = option.rect
            checkbox_option.state = QStyle.State_On if index.data() else QStyle.State_Off
            # 绘制元素的样式
            QApplication.style().drawControl(
                QStyle.CE_CheckBox, checkbox_option, painter)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        """
        同样是根据index 处理事件
        """
        if event.type() == QEvent.MouseButtonDblClick:
            return True
        if event.type() == QEvent.MouseButtonPress and index.column() == 0:
            print(
                f"Button clicked at row {index.row()} and column {index.column()}: {index.data()}")
            # 修改数据
            new_data = "New Data"
            model.setData(index, new_data, Qt.EditRole)
            return True
        if event.type() == QEvent.MouseButtonPress and index.column() == 1:
            current_value = index.data()
            model.setData(index, not current_value, Qt.EditRole)
            print(
                f"Checkbox at row {index.row()} toggled to {not current_value}")
            return True
        return super().editorEvent(event, model, option, index)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QTableView()
        self.model = self.create_model()
        self.table.setModel(self.model)

        self.table.setItemDelegate(MyDelegate())

        self.setCentralWidget(self.table)

    def create_model(self):
        model = QStandardItemModel(5, 2)
        model.setHorizontalHeaderLabels(["Button 1", "Button 2"])

        # 添加测试数据
        for row in range(5):
            item_button1 = QStandardItem("Button 1 Data") # 默认data
            item_button2 = QStandardItem("Button 2 Data")
            model.setItem(row, 0, item_button1)
            model.setItem(row, 1, item_button2)

        return model


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```