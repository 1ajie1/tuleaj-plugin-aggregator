import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    // 信号定义
    signal messageHidden()
    
    id: messageToast
    width: Math.max(280, Math.min(480, messageContent.implicitWidth + 40))  // 根据内容自动调整宽度，最小280，最大480
    height: messageContent.implicitHeight + 20
    z: 1000  // 确保在最上层
    color: messageType === "success" ? "#e8f5e8" : 
           messageType === "error" ? "#ffebee" : 
           messageType === "warning" ? "#fff3e0" : "#e3f2fd"
    radius: 8
    border.color: messageType === "success" ? "#4CAF50" : 
                  messageType === "error" ? "#f44336" : 
                  messageType === "warning" ? "#FF9800" : "#2196F3"
    border.width: 1
    
    // 阴影效果
    Rectangle {
        anchors.fill: parent
        anchors.margins: -2
        color: "transparent"
        border.color: "#40000000"
        border.width: 1
        radius: 10
        z: -1
    }
    
    // 消息内容
    RowLayout {
        id: messageContent
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // 确保布局能正确计算宽度
        Layout.preferredWidth: -1  // 让布局自动计算宽度
        
        // 图标
        Text {
            id: messageIcon
            text: messageType === "success" ? "✓" : 
                  messageType === "error" ? "✗" : 
                  messageType === "warning" ? "⚠" : "ℹ"
            font.pixelSize: 20
            font.bold: true
            color: messageType === "success" ? "#2E7D32" : 
                   messageType === "error" ? "#D32F2F" : 
                   messageType === "warning" ? "#F57C00" : "#1976D2"
            Layout.preferredWidth: 24
            Layout.alignment: Qt.AlignTop
        }
        
        // 消息文本
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4
            
            Text {
                id: messageTitle
                text: messageTitleText || ""
                font.pixelSize: 14
                font.bold: true
                color: messageType === "success" ? "#2E7D32" : 
                       messageType === "error" ? "#D32F2F" : 
                       messageType === "warning" ? "#F57C00" : "#1976D2"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.maximumWidth: 400  // 设置最大宽度，超出时换行
                visible: text !== ""
            }
            
            Text {
                id: messageText
                text: messageTextContent || ""
                font.pixelSize: 12
                color: "#333333"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.maximumWidth: 400  // 设置最大宽度，超出时换行
            }
        }
        
        // 关闭按钮
        Rectangle {
            id: closeButton
            width: 24
            height: 24
            color: closeButtonMouseArea.pressed ? "#40000000" : "transparent"
            radius: 12
            
            Text {
                anchors.centerIn: parent
                text: "×"
                font.pixelSize: 16
                font.bold: true
                color: "#666666"
            }
            
            MouseArea {
                id: closeButtonMouseArea
                anchors.fill: parent
                onClicked: {
                    messageToast.hide()
                }
            }
        }
    }
    
    // 属性
    property string messageType: "info"  // success, error, warning, info
    property string messageTitleText: ""
    property string messageTextContent: ""
    property int duration: 3000  // 显示持续时间（毫秒）
    
    // 动画
    property bool isVisible: false
    
    // 显示动画 - 从右侧滑入
    NumberAnimation {
        id: showAnimation
        target: messageToast
        property: "opacity"
        from: 0
        to: 1
        duration: 300
        easing.type: Easing.OutCubic
    }
    
    // 位置动画属性
    property real targetX: 0
    property real startX: 0
    
    NumberAnimation {
        id: showPositionAnimation
        target: messageToast
        property: "x"
        from: startX  // 从右侧屏幕外开始
        to: targetX   // 到目标位置
        duration: 300
        easing.type: Easing.OutCubic
    }
    
    NumberAnimation {
        id: showScaleAnimation
        target: messageToast
        property: "scale"
        from: 0.8
        to: 1.0
        duration: 300
        easing.type: Easing.OutCubic
    }
    
    // 隐藏动画 - 向上淡出
    NumberAnimation {
        id: hideAnimation
        target: messageToast
        property: "opacity"
        from: 1
        to: 0
        duration: 300
        easing.type: Easing.InCubic
        onFinished: {
            messageToast.visible = false
            messageToast.messageHidden()  // 发送隐藏信号
        }
    }
    
    NumberAnimation {
        id: hidePositionAnimation
        target: messageToast
        property: "y"
        from: messageToast.y
        to: messageToast.y - 50  // 向上移动
        duration: 300
        easing.type: Easing.InCubic
    }
    
    NumberAnimation {
        id: hideScaleAnimation
        target: messageToast
        property: "scale"
        from: 1.0
        to: 0.8
        duration: 300
        easing.type: Easing.InCubic
    }
    
    // 自动隐藏定时器
    Timer {
        id: autoHideTimer
        interval: messageToast.duration
        repeat: false
        onTriggered: {
            messageToast.hide()
        }
    }
    
    // 显示消息
    function show(type, title, text, duration, targetX, targetY) {
        console.log("MessageToast: 显示消息", type, title, text)
        messageToast.messageType = type || "info"
        messageToast.messageTitleText = title || ""
        messageToast.messageTextContent = text || ""
        messageToast.duration = duration || 3000
        
        // 重新计算宽度以适应内容
        messageToast.width = Math.max(280, Math.min(480, messageContent.implicitWidth + 40))
        
        messageToast.visible = true
        messageToast.opacity = 0
        messageToast.scale = 0.8
        
        // 设置目标位置
        if (targetX !== undefined) {
            messageToast.targetX = targetX
        }
        if (targetY !== undefined) {
            messageToast.y = targetY
        }
        
        // 计算起始位置 - 从右侧中间开始
        var parentWidth = messageToast.parent ? messageToast.parent.width : 0
        var startX = parentWidth - (messageToast.width / 2)
        
        console.log("MessageToast: 父容器宽度:", parentWidth, "消息宽度:", messageToast.width, "起始X:", startX)
        
        messageToast.startX = startX
        
        // 设置初始位置
        messageToast.x = startX
        
        console.log("MessageToast: 起始位置", startX, messageToast.y)
        console.log("MessageToast: 目标位置", messageToast.targetX, messageToast.y)
        console.log("MessageToast: 消息可见性", messageToast.visible)
        
        showAnimation.start()
        showPositionAnimation.start()
        showScaleAnimation.start()
        
        if (messageToast.duration > 0) {
            autoHideTimer.start()
        }
    }
    
    // 隐藏消息
    function hide() {
        autoHideTimer.stop()
        hideAnimation.start()
        hidePositionAnimation.start()
        hideScaleAnimation.start()
    }
    
    // 成功消息
    function showSuccess(title, text, duration) {
        show("success", title, text, duration)
    }
    
    // 错误消息
    function showError(title, text, duration) {
        show("error", title, text, duration)
    }
    
    // 警告消息
    function showWarning(title, text, duration) {
        show("warning", title, text, duration)
    }
    
    // 信息消息
    function showInfo(title, text, duration) {
        show("info", title, text, duration)
    }
}