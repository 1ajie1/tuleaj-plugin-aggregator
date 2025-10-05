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
    property string searchText: ""
    
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
                    id: searchInput
                    Layout.fillWidth: true
                    text: root.searchText === "" ? searchInput.placeholderText : root.searchText
                    color: root.searchText === "" ? "#666666" : "#333333"
                    font.pixelSize: 14
                    selectByMouse: true
                    
                    // 占位符文本
                    property string placeholderText: "搜索插件..."
                    
                    onTextChanged: {
                        // 只有当文本不是占位符时才进行搜索
                        if (text !== placeholderText) {
                            root.searchText = text
                            filterPlugins(text)
                        }
                    }
                    
                    // 当获得焦点时清空占位符
                    onActiveFocusChanged: {
                        if (activeFocus && text === placeholderText) {
                            text = ""
                        } else if (!activeFocus && text === "") {
                            text = placeholderText
                        }
                    }
                    
                    // 初始状态显示占位符
                    Component.onCompleted: {
                        if (text === "") {
                            text = placeholderText
                        }
                    }
                }
                
                // 清空搜索按钮
                Rectangle {
                    width: 20
                    height: 20
                    radius: 10
                    color: "#e0e0e0"
                    visible: root.searchText !== "" && root.searchText !== "搜索插件..."
                    
                    Text {
                        anchors.centerIn: parent
                        text: "✕"
                        font.pixelSize: 12
                        color: "#666666"
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            root.searchText = ""
                            searchInput.text = ""
                            searchInput.focus = false  // 移除焦点以触发占位符逻辑
                            filterPlugins("")
                        }
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
            
            // 原始插件数据模型
            ListModel {
                id: pluginListModel
                
                // 示例数据
                ListElement {
                    name: "Chrome Extension Tools"
                    status: "running"
                    icon: "🔧"
                }
                ListElement {
                    name: "Figma Plugin SDK"
                    status: "stopped"
                    icon: "⚡"
                }
                ListElement {
                    name: "Data Visualization"
                    status: "running"
                    icon: "📊"
                }
                ListElement {
                    name: "Package Manager"
                    status: "error"
                    icon: "📦"
                }
                ListElement {
                    name: "VSCode Extension Manager"
                    status: "running"
                    icon: "💻"
                }
                ListElement {
                    name: "Webpack Bundle Analyzer"
                    status: "stopped"
                    icon: "📊"
                }
                ListElement {
                    name: "ESLint Configuration"
                    status: "running"
                    icon: "🔍"
                }
                ListElement {
                    name: "Prettier Code Formatter"
                    status: "stopped"
                    icon: "✨"
                }
                ListElement {
                    name: "Git Integration"
                    status: "running"
                    icon: "🌿"
                }
                ListElement {
                    name: "Docker Container Manager"
                    status: "error"
                    icon: "🐳"
                }
                ListElement {
                    name: "API Testing Suite"
                    status: "stopped"
                    icon: "🔗"
                }
            }
            
            // 过滤后的插件模型
            ListModel {
                id: filteredPluginModel
            }
            
            ListView {
                id: pluginListView
                anchors.fill: parent
                anchors.rightMargin: 12  // 为滚动条留出空间
                spacing: 8
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.VerticalFlick
                model: filteredPluginModel
                
            delegate: PluginItem {
                width: pluginListView.width
                height: 70
                    
                    pluginName: model.name
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
        console.log("搜索:", searchText)
        
        // 清空过滤模型
        filteredPluginModel.clear()
        
        // 如果搜索文本为空或为占位符，显示所有插件
        if (searchText === "" || searchText === "搜索插件...") {
            // 复制所有插件到过滤模型
            for (var i = 0; i < pluginListModel.count; i++) {
                var plugin = pluginListModel.get(i)
                filteredPluginModel.append({
                    name: plugin.name,
                    description: plugin.description,
                    status: plugin.status,
                    icon: plugin.icon
                })
            }
        } else {
            // 根据搜索文本过滤插件
            var searchLower = searchText.toLowerCase()
            for (var i = 0; i < pluginListModel.count; i++) {
                var plugin = pluginListModel.get(i)
                var nameLower = plugin.name.toLowerCase()
                var descLower = plugin.description.toLowerCase()
                
                // 检查插件名称或描述是否包含搜索文本
                if (nameLower.indexOf(searchLower) !== -1 || descLower.indexOf(searchLower) !== -1) {
                    filteredPluginModel.append({
                        name: plugin.name,
                        description: plugin.description,
                        status: plugin.status,
                        icon: plugin.icon
                    })
                }
            }
        }
        
        console.log("过滤后插件数量:", filteredPluginModel.count)
    }
    
    // 初始化时显示所有插件
    Component.onCompleted: {
        filterPlugins("")
    }
}

