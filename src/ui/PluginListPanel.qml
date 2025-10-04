import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 300
    color: "#ffffff"
    
    // 信号定义
    signal pluginSelected(string pluginName)
    signal pluginStartRequested(string pluginName)
    signal pluginStopRequested(string pluginName)
    signal pluginUninstallRequested(string pluginName)
    
    // 属性
    property alias pluginList: pluginListModel
    property string selectedPlugin: ""
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16
        
        // 顶部标题区域
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            // 应用图标
            Rectangle {
                width: 32
                height: 32
                radius: 8
                color: "#4CAF50"
                
                Text {
                    anchors.centerIn: parent
                    text: "📦"
                    font.pixelSize: 16
                    color: "white"
                }
            }
            
            // 应用标题
            Text {
                text: "插件聚合器"
                font.pixelSize: 18
                font.bold: true
                color: "#333333"
            }
        }
        
        // 搜索框
        Rectangle {
            Layout.fillWidth: true
            height: 40
            radius: 20
            color: "#f5f5f5"
            border.color: "#e0e0e0"
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                
                Text {
                    text: "🔍"
                    font.pixelSize: 16
                    color: "#666666"
                }
                
                TextInput {
                    Layout.fillWidth: true
                    text: "搜索插件..."
                    color: "#666666"
                    font.pixelSize: 14
                    selectByMouse: true
                    
                    onTextChanged: {
                        // 实现搜索功能
                        filterPlugins(text)
                    }
                }
            }
        }
        
        // 插件列表
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            
            // 自定义滚动条容器
            Rectangle {
                id: scrollBarContainer
                width: 6
                height: parent.height - 8
                anchors.right: parent.right
                anchors.rightMargin: 2
                anchors.top: parent.top
                anchors.topMargin: 4
                color: "transparent"
                visible: pluginListView.contentHeight > pluginListView.height
                
                // 滚动条背景
                Rectangle {
                    id: scrollBarBackground
                    anchors.fill: parent
                    color: "#e8e8e8"
                    radius: 3
                    opacity: verticalScrollBarMouseArea.containsMouse ? 0.8 : 0.4
                    
                    Behavior on opacity {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }
                }
                
                // 滚动条滑块
                Rectangle {
                    id: scrollBarHandle
                    width: parent.width
                    height: Math.max(20, (pluginListView.height / pluginListView.contentHeight) * scrollBarContainer.height)
                    x: 0
                    y: (pluginListView.contentY / (pluginListView.contentHeight - pluginListView.height)) * 
                       (scrollBarContainer.height - height)
                    color: verticalScrollBarMouseArea.pressed ? "#1B5E20" : 
                           (verticalScrollBarMouseArea.containsMouse ? "#2E7D32" : "#4CAF50")
                    radius: 3
                    opacity: verticalScrollBarMouseArea.containsMouse ? 1.0 : 0.7
                    
                    // 渐变效果
                    gradient: Gradient {
                        GradientStop { 
                            position: 0.0; 
                            color: verticalScrollBarMouseArea.pressed ? "#0D4A0F" : 
                                   (verticalScrollBarMouseArea.containsMouse ? "#1B5E20" : "#4CAF50")
                        }
                        GradientStop { 
                            position: 1.0; 
                            color: verticalScrollBarMouseArea.pressed ? "#1B5E20" : 
                                   (verticalScrollBarMouseArea.containsMouse ? "#2E7D32" : "#66BB6A")
                        }
                    }
                    
                    // 内阴影效果
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 1
                        color: "transparent"
                        border.color: "white"
                        border.width: 1
                        radius: 2
                        opacity: 0.3
                    }
                    
                    // 动画效果
                    Behavior on opacity {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }
                    
                    Behavior on scale {
                        NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                    }
                    
                    scale: verticalScrollBarMouseArea.pressed ? 1.1 : 
                           (verticalScrollBarMouseArea.containsMouse ? 1.05 : 1.0)
                }
                
                // 鼠标交互区域
                MouseArea {
                    id: verticalScrollBarMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton
                    
                    onPressed: {
                        var clickY = mouseY
                        var handleY = scrollBarHandle.y
                        var handleHeight = scrollBarHandle.height
                        var containerHeight = scrollBarContainer.height
                        
                        if (clickY < handleY) {
                            // 点击滑块上方，向上滚动
                            pluginListView.contentY = Math.max(0, pluginListView.contentY - pluginListView.height * 0.8)
                        } else if (clickY > handleY + handleHeight) {
                            // 点击滑块下方，向下滚动
                            pluginListView.contentY = Math.min(pluginListView.contentHeight - pluginListView.height, 
                                                              pluginListView.contentY + pluginListView.height * 0.8)
                        } else {
                            // 点击滑块，开始拖拽
                            drag.target = scrollBarHandle
                            drag.axis = Drag.YAxis
                            drag.minimumY = 0
                            drag.maximumY = containerHeight - handleHeight
                        }
                    }
                    
                    onReleased: {
                        drag.target = null
                    }
                    
                    onPositionChanged: {
                        if (drag.target === scrollBarHandle) {
                            var ratio = scrollBarHandle.y / (scrollBarContainer.height - scrollBarHandle.height)
                            pluginListView.contentY = ratio * (pluginListView.contentHeight - pluginListView.height)
                        }
                    }
                }
            }
            
            ScrollBar.vertical: ScrollBar {
                id: verticalScrollBar
                policy: ScrollBar.AlwaysOff  // 隐藏默认滚动条
            }
            
            ListView {
                id: pluginListView
                anchors.fill: parent
                anchors.rightMargin: 12  // 为滚动条留出空间
                spacing: 8
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.VerticalFlick
                model: ListModel {
                    id: pluginListModel
                    
                    // 示例数据
                    ListElement {
                        name: "Chrome Extension Tools"
                        description: "Chrome浏览器扩展开发和调试工具, 提供实时监控和性能分析"
                        status: "running"
                        icon: "🔧"
                    }
                    ListElement {
                        name: "Figma Plugin SDK"
                        description: "Figma插件开发SDK, 包含完整的API文档和示例代码"
                        status: "stopped"
                        icon: "⚡"
                    }
                    ListElement {
                        name: "Data Visualization"
                        description: "数据可视化工具集, 支持多种图表类型和交互式分析"
                        status: "running"
                        icon: "📊"
                    }
                    ListElement {
                        name: "Package Manager"
                        description: "智能包管理器, 自动处理依赖关系和版本冲突"
                        status: "error"
                        icon: "📦"
                    }
                    ListElement {
                        name: "VSCode Extension Manager"
                        description: "管理和同步Visual Studio Code扩展,支持多设备同步和批量管理功能"
                        status: "running"
                        icon: "💻"
                    }
                    ListElement {
                        name: "Webpack Bundle Analyzer"
                        description: "分析Webpack打包结果,可视化展示bundle大小和依赖关系"
                        status: "stopped"
                        icon: "📊"
                    }
                    ListElement {
                        name: "ESLint Configuration"
                        description: "JavaScript代码质量检查工具,提供实时错误检测和修复建议"
                        status: "running"
                        icon: "🔍"
                    }
                    ListElement {
                        name: "Prettier Code Formatter"
                        description: "代码格式化工具,支持多种编程语言的自动格式化"
                        status: "stopped"
                        icon: "✨"
                    }
                    ListElement {
                        name: "Git Integration"
                        description: "Git版本控制集成工具,提供可视化的代码版本管理"
                        status: "running"
                        icon: "🌿"
                    }
                    ListElement {
                        name: "Docker Container Manager"
                        description: "Docker容器管理工具,简化容器生命周期管理"
                        status: "error"
                        icon: "🐳"
                    }
                    ListElement {
                        name: "API Testing Suite"
                        description: "RESTful API测试工具集,支持自动化测试和性能监控"
                        status: "stopped"
                        icon: "🔗"
                    }
                }
                
            delegate: PluginItem {
                width: pluginListView.width
                height: 70
                    
                    pluginName: model.name
                    pluginDescription: model.description
                    pluginStatus: model.status
                    pluginIcon: model.icon
                    isSelected: root.selectedPlugin === model.name
                    
                    onStartClicked: {
                        root.pluginStartRequested(model.name)
                    }
                    
                    onStopClicked: {
                        root.pluginStopRequested(model.name)
                    }
                    
                    onUninstallClicked: {
                        root.pluginUninstallRequested(model.name)
                    }
                    
                    onItemClicked: {
                        root.selectedPlugin = model.name
                        root.pluginSelected(model.name)
                    }
                }
            }
        }
    }
    
    // 搜索过滤函数
    function filterPlugins(searchText) {
        // 这里可以实现搜索过滤逻辑
        console.log("搜索:", searchText)
    }
}

