---
title: JOSM 中自定义开发
date: 2025-06-26 16:01:52
tags:
    - java  
    - josm
---

在对JOSM 进行二次开发时的一些笔记，包含Action和Dialog 等。  
<!-- more -->

## Action    
在JOSM 中可以通过在菜单栏中添加`Action` 来实现自定义功能。
```java
// 忽略导包过程
public class AdjacentNodesAction extends JosmAction {

    public static final boolean treeMode = false;

    public AdjacentNodesAction() {
        super(tr("名称"), // 在菜单栏中显示的名称
              "图标名称", // 图标在resources/images 中
              tr("提示信息"),  // 注册快捷键
              Shortcut.registerShortcut("主菜单名:名称","说明信息",
                        KeyEvent.VK_E, Shortcut.DIRECT), true);  // 快捷键
        putValue("help", ht("/Action/AdjacentNodes"));  // 添加帮助信息
    }

    private transient Set<Way> activeWays = new HashSet<>();

    @Override
    public void actionPerformed(ActionEvent e) {
        // action 执行的操作，重中之重

        // 1. 通过曾管理器获取当前激活的数据集
        DataSet ds = getLayerManager().getActiveDataSet();  
        // 2. 获取当前选中的元素，可以是点、路线或者是关系
        Collection<Node> selectedNodes = ds.getSelectedNodes();
        Set<Way> selectedWays = new LinkedHashSet<>(ds.getSelectedWays());

        // 判断为空
        if (selectedNodes.isEmpty() && selectedWays.isEmpty()) return;

        if (selectedWays.isEmpty()) {
            // 判断为空
        } else {
            activeWays = selectedWays;
        }

        // 随后可以对所选数据进行一系列操作，甚至是新增不存在的元素

        // 如果需要创建对话框的话
        LatLonDialog dialog = new LatLonDialog(MainApplication.getMainFrame(), tr("Add Node..."), ht("/Action/AddNode"));
        dialog.showDialog();  // 在主窗口显示对话框，该操作会阻塞主界面

    }


    @Override
    protected void updateEnabledState() {
        // 所选层变化时更新
        updateEnabledStateOnCurrentSelection();
    }

    @Override
    protected void updateEnabledState(Collection<? extends OsmPrimitive> selection) {
        // 所选元素变化时更新，一般默认如下操作即可  
        // setEnabled(selection != null && !selection.isEmpty());
        // 如果有暂存数据则需清空，如下：
        boolean hasSel = selection != null && !selection.isEmpty();
        if (!hasSel && activeWays != null) {
            // 清空激活Ways
            activeWays.clear();
        }
        setEnabled(hasSel);
    }
}
```

### 定义对话框  
```java
public class LatLonDialog extends ExtendedDialog{
    // ...
}
```

### 添加菜单项
定义完成后即可在`MainMenu.java` 中便可以新增元素：  
```java
public class MainMenu extends JMenuBar{
    public void Initialize(){
        // ...  
        selectionMenu.addSeparator();
        add(selectionMenu, new SelectWayNodesAction());
        // ...
    }
}
```

## 可折叠对话框  
```java
public class MeasurementDialog extends ToggleDialog implements DataSelectionListener { 
    // 可以继承不只一个接口用于监听事件
    public MeasurementDialog()
    {
        // 构造窗口，类似于Action  
        super(tr("测量数据"), "measure", tr("打开测量窗口"),
                Shortcut.registerShortcut("subwindow:measurement", tr("窗口: {0}", tr("测量数据")),
                        KeyEvent.VK_U, Shortcut.CTRL_SHIFT), 150);

        // 元素布局  

        // 添加事件监听
        MainApplication.getLayerManager().addLayerChangeListener(this);
        SelectionEventManager.getInstance().addSelectionListener(this);
        SystemOfMeasurement.addSoMChangeListener(this);
    }
    
    @Override
    public void selectionChanged(SelectionChangeEvent event) {
        // 处理选中元素变化
        refresh(event.getSelection());
    }
    
    @Override
    public void destroy() {
        // 析构函数，移除事件监听和其他资源
        super.destroy();
        SystemOfMeasurement.removeSoMChangeListener(this);
        SelectionEventManager.getInstance().removeSelectionListener(this);
        MainApplication.getLayerManager().removeLayerChangeListener(this);
    }
    // 按需重写各类监听
    // @Override public void nodeMoved(NodeMovedEvent event) { }
    // ...
}
```

可以在`MainFrame.java` 中注册使用：  
```java
public class MapFrame extends JPanel implements Destroyable, ActiveLayerChangeListener, LayerChangeListener {
    public MapFrame(ViewportData viewportData) {
        // ...
        measurementDialog = new MeasurementDialog();
        addToggleDialog(measurementDialog);
        // ...
    }
}
```



## 参考资料  
1. [github.com/JOSM/josm-plugins](https://github.com/JOSM/josm-plugins/tree/master/utilsplugin2)