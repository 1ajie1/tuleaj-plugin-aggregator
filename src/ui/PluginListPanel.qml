import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import PluginBridge 1.0

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

    // 消息管理器引用
    property var messageManager: null

    // 消息去重机制
    property var lastMessages: ({})
    property int messageCooldown: 2000  // 2秒内不重复显示相同消息

    // 注意：不再创建新的PluginBridge实例，使用main.py传递的全局实例
    // 全局pluginBridge实例通过main.py的setContextProperty传递

    // 连接全局pluginBridge的信号并初始化
    Component.onCompleted: {
        // 1. 连接全局pluginBridge信号
        if (pluginBridge) {
            console.log("PluginListPanel: 连接全局pluginBridge信号");

            // 连接信号
            pluginBridge.pluginsLoaded.connect(function (plugins) {
                console.log("插件加载完成，共", plugins.length, "个插件");
                updatePluginList(plugins);
            });

            pluginBridge.pluginStatusChanged.connect(function (pluginName, status) {
                console.log("插件状态变化:", pluginName, status);
                updatePluginStatus(pluginName, status);

                // 使用安全消息显示，避免重复通知
                switch (status) {
                case "running":
                    safeShowMessage("success", "插件启动成功", pluginName + " 已成功启动", 3000, "start_success_" + pluginName);
                    break;
                case "stopped":
                    safeShowMessage("info", "插件已停止", pluginName + " 已停止运行", 2000, "stop_success_" + pluginName);
                    break;
                case "error":
                    safeShowMessage("error", "插件运行错误", pluginName + " 运行出现错误", 5000, "error_" + pluginName);
                    break;
                case "starting":
                    // 启动中状态不显示通知，避免干扰
                    break;
                }
            });

            pluginBridge.pluginError.connect(function (pluginName, error) {
                console.log("插件错误:", pluginName, error);
                // 只在非error状态时显示错误通知，避免与状态变化通知重复
                var currentStatus = getPluginStatus(pluginName);
                if (currentStatus !== "error") {
                    safeShowMessage("error", "插件操作失败", pluginName + ": " + error, 5000, "operation_error_" + pluginName);
                }
            });

            pluginBridge.dependencyInstalling.connect(function (pluginName, message) {
                console.log("依赖安装中:", pluginName, message);
            // 依赖安装过程不显示通知，避免干扰
            });

            pluginBridge.dependencyInstalled.connect(function (envName, packageName, success, message) {
                console.log("依赖安装完成:", envName, packageName, success, message);
                if (success) {
                    safeShowMessage("success", "依赖安装完成", packageName + " 安装成功", 3000, "dep_install_" + packageName);
                } else {
                    safeShowMessage("error", "依赖安装失败", packageName + " 安装失败", 5000, "dep_error_" + packageName);
                }
            });

            pluginBridge.dependencySyncCompleted.connect(function (envName, success, message) {
                console.log("依赖同步完成:", envName, success, message);
                if (success) {
                    safeShowMessage("success", "依赖同步完成", "环境 " + " 同步成功", 3000);
                } else {
                    safeShowMessage("error", "依赖同步失败", "环境 " + " 同步失败", 5000);
                }
            });

            console.log("PluginListPanel: 全局pluginBridge信号连接完成");
        } else {
            console.error("PluginListPanel: 全局pluginBridge不可用");
        }

        // 2. 初始化时显示所有插件
        filterPlugins("");
    }

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
                    text: "搜索"
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
                            root.searchText = text;
                            filterPlugins(text);
                        }
                    }

                    // 当获得焦点时清空占位符
                    onActiveFocusChanged: {
                        if (activeFocus && text === placeholderText) {
                            text = "";
                        } else if (!activeFocus && text === "") {
                            text = placeholderText;
                        }
                    }

                    // 初始状态显示占位符
                    Component.onCompleted: {
                        if (text === "") {
                            text = placeholderText;
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
                            root.searchText = "";
                            searchInput.text = "";
                            searchInput.focus = false;  // 移除焦点以触发占位符逻辑
                            filterPlugins("");
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
                visible: false
                // visible: pluginListView.contentHeight > pluginListView.height

                // 滚动条背景
                Rectangle {
                    id: scrollBarBackground
                    anchors.fill: parent
                    color: "#e8e8e8"
                    radius: 3
                    opacity: verticalScrollBarMouseArea.containsMouse ? 0.8 : 0.4

                    Behavior on opacity {
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.OutCubic
                        }
                    }
                }

                // 滚动条滑块
                Rectangle {
                    id: scrollBarHandle
                    width: parent.width
                    height: Math.max(20, (pluginListView.height / pluginListView.contentHeight) * scrollBarContainer.height)
                    x: 0
                    y: (pluginListView.contentY / (pluginListView.contentHeight - pluginListView.height)) * (scrollBarContainer.height - height)
                    color: verticalScrollBarMouseArea.pressed ? "#1B5E20" : (verticalScrollBarMouseArea.containsMouse ? "#2E7D32" : "#4CAF50")
                    radius: 3
                    opacity: verticalScrollBarMouseArea.containsMouse ? 1.0 : 0.7

                    // 渐变效果
                    gradient: Gradient {
                        GradientStop {
                            position: 0.0
                            color: verticalScrollBarMouseArea.pressed ? "#0D4A0F" : (verticalScrollBarMouseArea.containsMouse ? "#1B5E20" : "#4CAF50")
                        }
                        GradientStop {
                            position: 1.0
                            color: verticalScrollBarMouseArea.pressed ? "#1B5E20" : (verticalScrollBarMouseArea.containsMouse ? "#2E7D32" : "#66BB6A")
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
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.OutCubic
                        }
                    }

                    Behavior on scale {
                        NumberAnimation {
                            duration: 150
                            easing.type: Easing.OutCubic
                        }
                    }

                    scale: verticalScrollBarMouseArea.pressed ? 1.1 : (verticalScrollBarMouseArea.containsMouse ? 1.05 : 1.0)
                }

                // 鼠标交互区域
                MouseArea {
                    id: verticalScrollBarMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton

                    onPressed: {
                        var clickY = mouseY;
                        var handleY = scrollBarHandle.y;
                        var handleHeight = scrollBarHandle.height;
                        var containerHeight = scrollBarContainer.height;

                        if (clickY < handleY) {
                            // 点击滑块上方，向上滚动
                            pluginListView.contentY = Math.max(0, pluginListView.contentY - pluginListView.height * 0.8);
                        } else if (clickY > handleY + handleHeight) {
                            // 点击滑块下方，向下滚动
                            pluginListView.contentY = Math.min(pluginListView.contentHeight - pluginListView.height, pluginListView.contentY + pluginListView.height * 0.8);
                        } else {
                            // 点击滑块，开始拖拽
                            drag.target = scrollBarHandle;
                            drag.axis = Drag.YAxis;
                            drag.minimumY = 0;
                            drag.maximumY = containerHeight - handleHeight;
                        }
                    }

                    onReleased: {
                        drag.target = null;
                    }

                    onPositionChanged: {
                        if (drag.target === scrollBarHandle) {
                            var ratio = scrollBarHandle.y / (scrollBarContainer.height - scrollBarHandle.height);
                            pluginListView.contentY = ratio * (pluginListView.contentHeight - pluginListView.height);
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
                        console.log("启动插件:", model.name);
                        pluginBridge.start_plugin(model.name);
                        root.pluginStartRequested(model.name);
                    }

                    onStopClicked: {
                        console.log("停止插件:", model.name);
                        pluginBridge.stop_plugin(model.name);
                        root.pluginStopRequested(model.name);
                    }

                    onUninstallClicked: {
                        console.log("卸载插件:", model.name);
                        pluginBridge.uninstall_plugin(model.name);
                        root.pluginUninstallRequested(model.name);
                    }

                    onItemClicked: {
                        console.log("选择插件:", model.name);
                        root.selectedPlugin = model.name;
                        root.pluginSelected(model.name);
                    }
                }
            }
        }
    }

    // 更新插件列表
    function updatePluginList(plugins) {
        console.log("更新插件列表，插件数量:", plugins.length);

        // 清空现有数据
        pluginListModel.clear();

        // 添加新数据
        for (var i = 0; i < plugins.length; i++) {
            var plugin = plugins[i];
            pluginListModel.append({
                name: plugin.name || "",
                description: plugin.description || "",
                status: plugin.status || "stopped",
                icon: plugin.icon || "📦",
                version: plugin.version || "1.0.0",
                author: plugin.author || "",
                path: plugin.path || ""
            });
        }

        // 重新过滤显示
        filterPlugins(searchText);
    }

    // 更新插件状态
    function updatePluginStatus(pluginName, status) {
        console.log("更新插件状态:", pluginName, "->", status);

        // 更新原始模型
        for (var i = 0; i < pluginListModel.count; i++) {
            var plugin = pluginListModel.get(i);
            if (plugin.name === pluginName) {
                pluginListModel.setProperty(i, "status", status);
                console.log("原始模型状态已更新");
                break;
            }
        }

        // 更新过滤模型中的对应项
        for (var j = 0; j < filteredPluginModel.count; j++) {
            var filteredPlugin = filteredPluginModel.get(j);
            if (filteredPlugin.name === pluginName) {
                filteredPluginModel.setProperty(j, "status", status);
                console.log("过滤模型状态已更新");
                break;
            }
        }
    }

    // 搜索过滤函数
    function filterPlugins(searchText) {
        console.log("搜索:", searchText);

        // 清空过滤模型
        filteredPluginModel.clear();

        // 如果搜索文本为空或为占位符，显示所有插件
        if (searchText === "") {
            // 复制所有插件到过滤模型
            for (var i = 0; i < pluginListModel.count; i++) {
                var plugin = pluginListModel.get(i);
                filteredPluginModel.append({
                    name: plugin.name,
                    description: plugin.description,
                    status: plugin.status,
                    icon: plugin.icon
                });
            }
        } else {
            // 根据搜索文本过滤插件
            var searchLower = searchText.toLowerCase();
            for (var i = 0; i < pluginListModel.count; i++) {
                var plugin = pluginListModel.get(i);
                var nameLower = plugin.name.toLowerCase();
                var descLower = plugin.description.toLowerCase();

                // 检查插件名称或描述是否包含搜索文本
                if (nameLower.indexOf(searchLower) !== -1 || descLower.indexOf(searchLower) !== -1) {
                    filteredPluginModel.append({
                        name: plugin.name,
                        description: plugin.description,
                        status: plugin.status,
                        icon: plugin.icon
                    });
                }
            }
        }

        console.log("过滤后插件数量:", filteredPluginModel.count);
    }

    // 获取插件当前状态
    function getPluginStatus(pluginName) {
        for (var i = 0; i < pluginListModel.count; i++) {
            var plugin = pluginListModel.get(i);
            if (plugin.name === pluginName) {
                return plugin.status;
            }
        }
        return "unknown";
    }

    // 消息去重函数
    function shouldShowMessage(messageKey) {
        var now = Date.now();
        var lastTime = lastMessages[messageKey] || 0;

        if (now - lastTime > messageCooldown) {
            lastMessages[messageKey] = now;
            return true;
        }
        return false;
    }

    // 安全显示消息
    function safeShowMessage(type, title, message, duration, messageKey) {
        if (messageManager && shouldShowMessage(messageKey || (title + ":" + message))) {
            switch (type) {
            case "success":
                messageManager.showSuccess(title, message, duration || 3000);
                break;
            case "error":
                messageManager.showError(title, message, duration || 5000);
                break;
            case "warning":
                messageManager.showWarning(title, message, duration || 4000);
                break;
            case "info":
            default:
                messageManager.showInfo(title, message, duration || 2000);
                break;
            }
        }
    }

    // 这些函数已被消息管理器替代，保留用于兼容性
}
