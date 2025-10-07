import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtWebEngine 1.15
import PluginBridge 1.0

Rectangle {
    id: root
    color: "#ffffff"
    
    // 属性
    property string currentPluginName: ""
    property bool isLoading: false
    property string errorMessage: ""
    property Timer loadingTimer: Timer {
        interval: 10000  // 10秒超时
        repeat: false
        onTriggered: {
            if (root.isLoading) {
                console.log("PluginDocumentViewer: 加载超时")
                root.isLoading = false
                root.errorMessage = "文档加载超时，请重试"
            }
        }
    }
    
    // 信号定义
    signal settingsRequested
    signal addPluginRequested
    
    // README.md 信号处理
    function onReadmeLoaded(pluginName, htmlFilePath) {
        console.log("PluginDocumentViewer: 收到 README.md 加载完成信号:", pluginName)
        console.log("PluginDocumentViewer: HTML 文件路径:", htmlFilePath)
        if (pluginName === currentPluginName) {
            console.log("PluginDocumentViewer: 插件名称匹配，加载 HTML 文件")
            isLoading = false
            loadingTimer.stop()
            errorMessage = ""
            webView.url = "file:///" + htmlFilePath.replace(/\\/g, "/")
        } else {
            console.log("PluginDocumentViewer: 插件名称不匹配，当前:", currentPluginName, "收到:", pluginName)
        }
    }
    
    function onReadmeError(pluginName, errorMsg) {
        console.log("PluginDocumentViewer: 收到 README.md 加载错误信号:", pluginName, errorMsg)
        if (pluginName === currentPluginName) {
            isLoading = false
            loadingTimer.stop()
            errorMessage = errorMsg
        }
    }

    // 函数：加载插件文档
    function loadPluginDocument(pluginName) {
        console.log("PluginDocumentViewer: loadPluginDocument called with:", pluginName);
        currentPluginName = pluginName;
        isLoading = true;
        errorMessage = "";
        
        // 启动超时计时器
        loadingTimer.start();
        
        // 调用后端生成 HTML 文件
        if (typeof pluginBridge !== 'undefined' && pluginBridge !== null) {
            console.log("PluginDocumentViewer: 调用 pluginBridge.generate_readme_html");
            pluginBridge.generate_readme_html(pluginName);
        } else {
            console.log("PluginDocumentViewer: pluginBridge 不可用");
            isLoading = false;
            loadingTimer.stop();
            errorMessage = "插件桥接器不可用";
        }
    }
    
    // 组件完成时连接信号
    Component.onCompleted: {
        console.log("PluginDocumentViewer: 组件创建完成")
        // 延迟连接信号，确保 pluginBridge 可用
        Qt.callLater(function() {
            if (typeof pluginBridge !== 'undefined' && pluginBridge !== null) {
                console.log("PluginDocumentViewer: 直接连接 pluginBridge 信号")
                pluginBridge.readmeLoaded.connect(root.onReadmeLoaded)
                pluginBridge.readmeError.connect(root.onReadmeError)
                console.log("PluginDocumentViewer: 信号连接完成")
            } else {
                console.log("PluginDocumentViewer: pluginBridge 不可用")
            }
        })
    }
    
    // 主布局
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // 主要内容区域
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            
            StackLayout {
                id: documentStackLayout
                anchors.fill: parent
                anchors.rightMargin: 12  // 为滚动条留出空间
                currentIndex: {
                    if (isLoading) return 0;
                    if (errorMessage.length > 0) return 1;
                    return 2;
                }
                
                // 加载状态
                Rectangle {
                    color: "transparent"
                    
                    Column {
                        anchors.centerIn: parent
                        spacing: 16
                        
                        BusyIndicator {
                            anchors.horizontalCenter: parent.horizontalCenter
                            running: root.isLoading
                            width: 32
                            height: 32
                        }
                        
                    Text {
                            text: "正在加载文档..."
                            anchors.horizontalCenter: parent.horizontalCenter
                        color: "#666666"
                            font.pixelSize: 14
                        }
                    }
                }
                
                // 错误状态
                Rectangle {
                    color: "transparent"
                    
                    Column {
                        anchors.centerIn: parent
                        spacing: 16
                        
                        Text {
                            text: "⚠️"
                            anchors.horizontalCenter: parent.horizontalCenter
                            font.pixelSize: 32
                        }
                        
                        Text {
                            text: "文档加载失败"
                            anchors.horizontalCenter: parent.horizontalCenter
                            color: "#e74c3c"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        Text {
                            text: root.errorMessage || "请检查文件是否存在"
                            anchors.horizontalCenter: parent.horizontalCenter
                            color: "#666666"
                            font.pixelSize: 14
                            wrapMode: Text.WordWrap
                            width: Math.min(parent.width - 32, 400)
                        }
                        
                        Button {
                            text: "重试"
                            anchors.horizontalCenter: parent.horizontalCenter
                            onClicked: {
                                if (currentPluginName.length > 0) {
                                    loadPluginDocument(currentPluginName);
                                }
                            }
                        }
                    }
                }
                
                // 内容显示 - 使用 Flickable + 自定义滚动条（参考 SettingsWindow）
                Flickable {
                    id: documentFlickable
                    anchors.fill: parent
                    contentWidth: webView.width
                    contentHeight: webView.height
                    boundsBehavior: Flickable.StopAtBounds
                    flickableDirection: Flickable.VerticalFlick
                    
                    WebEngineView {
                        id: webView
                        width: documentFlickable.width
                        height: Math.max(documentFlickable.height, implicitHeight)
                        
                        // 设置背景为白色
                        backgroundColor: "white"
                        
                        // 设置权限
                        settings.javascriptEnabled: true
                        settings.localContentCanAccessRemoteUrls: false
                        settings.localContentCanAccessFileUrls: true
                        
                        // 禁用 WebEngineView 的内部滚动条
                        settings.autoLoadImages: true
                        settings.pluginsEnabled: false
                        
                        // 页面加载完成处理
                        onLoadingChanged: function(loadRequest) {
                            console.log("WebEngineView: 加载状态变化:", loadRequest.status)
                            if (loadRequest.status === WebEngineView.LoadSucceededStatus) {
                                console.log("WebEngineView: 页面加载成功")
                                // 注入 CSS 隐藏内部滚动条
                                webView.runJavaScript(`
                                    var style = document.createElement('style');
                                    style.innerHTML = 'body::-webkit-scrollbar { display: none; } html::-webkit-scrollbar { display: none; }';
                                    document.head.appendChild(style);
                                `)
                            } else if (loadRequest.status === WebEngineView.LoadFailedStatus) {
                                console.log("WebEngineView: 页面加载失败")
                                root.errorMessage = "页面加载失败"
                                root.isLoading = false
                            }
                        }
                        
                        // 当内容高度变化时更新 Flickable
                        onHeightChanged: {
                            documentFlickable.contentHeight = height
                        }
                    }
                }
            }
            
            // 自定义滚动条容器（备用方案）
            Rectangle {
                id: documentScrollBarContainer
                width: 6
                height: parent.height - 8
                anchors.right: parent.right
                anchors.rightMargin: 2
                anchors.top: parent.top
                anchors.topMargin: 4
                color: "transparent"
                visible: documentFlickable.contentHeight > documentFlickable.height
                
                // 滚动条背景
                Rectangle {
                    id: documentScrollBarBackground
                    anchors.fill: parent
                    color: "#e8e8e8"
                    radius: 3
                    opacity: documentScrollBarMouseArea.containsMouse ? 0.8 : 0.4
                    
                    Behavior on opacity {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }
                }
                
                // 滚动条滑块
                Rectangle {
                    id: documentScrollBarHandle
                    width: parent.width
                    height: Math.max(20, (documentFlickable.height / documentFlickable.contentHeight) * documentScrollBarContainer.height)
                    x: 0
                    y: (documentFlickable.contentY / (documentFlickable.contentHeight - documentFlickable.height)) * 
                       (documentScrollBarContainer.height - height)
                    color: documentScrollBarMouseArea.pressed ? "#1B5E20" : 
                           (documentScrollBarMouseArea.containsMouse ? "#2E7D32" : "#4CAF50")
                    radius: 3
                    opacity: documentScrollBarMouseArea.containsMouse ? 1.0 : 0.7
                    
                    // 渐变效果
                    gradient: Gradient {
                        GradientStop { 
                            position: 0.0; 
                            color: documentScrollBarMouseArea.pressed ? "#0D4A0F" : 
                                   (documentScrollBarMouseArea.containsMouse ? "#1B5E20" : "#4CAF50")
                        }
                        GradientStop { 
                            position: 1.0; 
                            color: documentScrollBarMouseArea.pressed ? "#1B5E20" : 
                                   (documentScrollBarMouseArea.containsMouse ? "#2E7D32" : "#66BB6A")
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
                    
                    scale: documentScrollBarMouseArea.pressed ? 1.1 : 
                           (documentScrollBarMouseArea.containsMouse ? 1.05 : 1.0)
                }
                
                // 鼠标交互区域
                MouseArea {
                    id: documentScrollBarMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton
                    
                    onPressed: {
                        var clickY = mouseY
                        var handleY = documentScrollBarHandle.y
                        var handleHeight = documentScrollBarHandle.height
                        var containerHeight = documentScrollBarContainer.height
                        
                        if (clickY < handleY) {
                            // 点击滑块上方，向上滚动
                            documentFlickable.contentY = Math.max(0, documentFlickable.contentY - documentFlickable.height * 0.8)
                        } else if (clickY > handleY + handleHeight) {
                            // 点击滑块下方，向下滚动
                            documentFlickable.contentY = Math.min(documentFlickable.contentHeight - documentFlickable.height, 
                                                                  documentFlickable.contentY + documentFlickable.height * 0.8)
                        } else {
                            // 点击滑块，开始拖拽
                            drag.target = documentScrollBarHandle
                            drag.axis = Drag.YAxis
                            drag.minimumY = 0
                            drag.maximumY = containerHeight - handleHeight
                        }
                    }
                    
                    onReleased: {
                        drag.target = null
                    }
                    
                    onPositionChanged: {
                        if (drag.target === documentScrollBarHandle) {
                            var ratio = documentScrollBarHandle.y / (documentScrollBarContainer.height - documentScrollBarHandle.height)
                            documentFlickable.contentY = ratio * (documentFlickable.contentHeight - documentFlickable.height)
                        }
                    }
                }
            }
        }
        
        // 右侧浮动操作按钮
        Rectangle {
            width: 60
            Layout.fillHeight: true
            color: "transparent"
            
            ColumnLayout {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12
                
                // 设置按钮
                Rectangle {
                    id: settingsButton
                    width: 40
                    height: 40
                    radius: 20
                    color: "#f5f5f5"
                    border.color: "#e0e0e0"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "⚙️"
                        font.pixelSize: 16
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            root.settingsRequested();
                        }
                        
                        onEntered: {
                            settingsButton.color = "#e8e8e8";
                            settingsButton.border.color = "#d0d0d0";
                        }
                        
                        onExited: {
                            settingsButton.color = "#f5f5f5";
                            settingsButton.border.color = "#e0e0e0";
                        }
                        
                        onPressed: {
                            settingsButton.color = "#d0d0d0";
                            settingsButton.border.color = "#c0c0c0";
                        }
                        
                        onReleased: {
                            settingsButton.color = "#e8e8e8";
                            settingsButton.border.color = "#d0d0d0";
                        }
                    }
                }
                
                // 添加插件按钮
                Rectangle {
                    id: addPluginButton
                    width: 40
                    height: 40
                    radius: 20
                    color: "#4CAF50"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "+"
                        font.pixelSize: 20
                        font.bold: true
                        color: "white"
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            root.addPluginRequested();
                        }
                        
                        onEntered: {
                            addPluginButton.color = "#45a049";
                        }
                        
                        onExited: {
                            addPluginButton.color = "#4CAF50";
                        }
                        
                        onPressed: {
                            addPluginButton.color = "#3d8b40";
                        }
                        
                        onReleased: {
                            addPluginButton.color = "#45a049";
                        }
                    }
                }
            }
        }
    }
}
