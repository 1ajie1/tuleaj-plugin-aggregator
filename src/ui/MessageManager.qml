import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: messageManager
    anchors.fill: parent
    z: 999  // 确保消息管理器在最上层
    
    // 消息队列
    property var messageQueue: []
    property int maxMessages: 5  // 最多同时显示5个消息
    property int messageSpacing: 10  // 消息间距
    property int rightMargin: 20  // 距离右边的距离
    
    // 当前显示的消息列表
    property var currentMessages: []
    
    // 监听窗口大小变化
    onWidthChanged: {
        rearrangeMessages()
    }
    
    // 添加消息到队列
    function addMessage(type, title, text, duration) {
        var message = {
            type: type || "info",
            title: title || "",
            text: text || "",
            duration: duration || 3000,
            id: Date.now() + Math.random()  // 唯一ID
        }
        
        messageQueue.push(message)
        processQueue()
    }
    
    // 处理消息队列
    function processQueue() {
        // 如果当前显示的消息数量小于最大值，且队列中有消息
        if (currentMessages.length < maxMessages && messageQueue.length > 0) {
            var message = messageQueue.shift()
            showMessage(message)
        }
    }
    
    // 显示消息
    function showMessage(message) {
        console.log("MessageManager: 尝试显示消息:", message.title, message.text)
        var messageComponent = Qt.createComponent("MessageToast.qml")
        console.log("MessageManager: 组件状态:", messageComponent.status)
        
        if (messageComponent.status === Component.Ready) {
            var messageToast = messageComponent.createObject(messageManager)
            console.log("MessageManager: 消息组件创建:", messageToast !== null)
            
            if (messageToast) {
                // 计算位置 - 右侧显示，新消息在下
                var yPosition = calculateMessagePosition()
                var xPosition = calculateMessageXPosition()
                console.log("MessageManager: 消息位置:", xPosition, yPosition)
                
                // 设置消息内容
                messageToast.messageType = message.type
                messageToast.messageTitleText = message.title
                messageToast.messageTextContent = message.text
                messageToast.duration = message.duration
                
                // 添加到当前消息列表（新消息添加到末尾）
                currentMessages.push({
                    id: message.id,
                    component: messageToast
                })
                
                console.log("MessageManager: 当前消息数量:", currentMessages.length)
                
                // 显示消息（位置在show函数中设置）
                messageToast.show(message.type, message.title, message.text, message.duration, xPosition, yPosition)
                
                // 设置消息隐藏回调
                messageToast.messageHidden.connect(function() {
                    removeMessage(message.id)
                })
            }
        } else {
            console.log("MessageManager: 组件创建失败:", messageComponent.errorString())
        }
    }
    
    // 计算消息X位置 - 右侧显示
    function calculateMessageXPosition() {
        var messageWidth = 280
        var availableWidth = messageManager.width
        var xPosition = availableWidth - messageWidth - rightMargin + 10
        
        console.log("MessageManager: 窗口宽度:", availableWidth, "消息宽度:", messageWidth, "计算X位置:", xPosition)
        
        // 确保消息不会超出左边界
        return Math.max(rightMargin, xPosition)
    }
    
    // 计算消息Y位置 - 从窗口中间开始，新消息在下，旧消息在上
    function calculateMessagePosition() {
        var availableHeight = messageManager.height
        var messageHeight = 80  // 固定消息高度
        var totalHeight = 0
        
        // 计算所有现有消息的总高度
        for (var i = 0; i < currentMessages.length; i++) {
            var msg = currentMessages[i]
            if (msg.component) {
                totalHeight += messageHeight + messageSpacing
            }
        }
        
        // 从窗口中间开始，向下偏移现有消息的高度
        var centerY = availableHeight / 2
        var yPosition = centerY + totalHeight
        
        console.log("MessageManager: 窗口高度:", availableHeight, "中心Y:", centerY, "总高度:", totalHeight, "计算Y位置:", yPosition)
        
        // 确保消息不会超出底部
        return Math.min(availableHeight - messageHeight - 20, yPosition)
    }
    
    // 移除消息
    function removeMessage(messageId) {
        for (var i = 0; i < currentMessages.length; i++) {
            if (currentMessages[i].id === messageId) {
                var messageToast = currentMessages[i].component
                if (messageToast) {
                    messageToast.destroy()
                }
                currentMessages.splice(i, 1)
                break
            }
        }
        
        // 重新排列剩余消息的位置
        rearrangeMessages()
        
        // 处理队列中的下一个消息
        processQueue()
    }
    
    // 重新排列消息位置 - 从中间开始，旧消息向上移动
    function rearrangeMessages() {
        var centerY = messageManager.height / 2
        var messageHeight = 80  // 固定消息高度
        var currentY = centerY
        
        // 从第一个消息开始向下排列
        for (var i = 0; i < currentMessages.length; i++) {
            var msg = currentMessages[i]
            if (msg.component) {
                var xPosition = calculateMessageXPosition()
                msg.component.x = xPosition
                
                var targetY = currentY
                msg.component.y = targetY
                
                currentY = targetY + messageHeight + messageSpacing
            }
        }
    }
    
    // 动画移动消息位置
    function animateMessagePosition(messageToast, targetY) {
        // 直接使用属性动画
        var animation = Qt.createQmlObject('
            import QtQuick 2.15
            NumberAnimation {
                id: positionAnim
                target: messageToast
                property: "y"
                to: targetY
                duration: 300
                easing.type: Easing.OutCubic
                onFinished: {
                    positionAnim.destroy()
                }
            }
        ', messageManager, "PositionAnimation")
        
        animation.start()
    }
    
    // 便捷方法
    function showSuccess(title, text, duration) {
        addMessage("success", title, text, duration)
    }
    
    function showError(title, text, duration) {
        addMessage("error", title, text, duration)
    }
    
    function showWarning(title, text, duration) {
        addMessage("warning", title, text, duration)
    }
    
    function showInfo(title, text, duration) {
        addMessage("info", title, text, duration)
    }
    
    // 清除所有消息
    function clearAll() {
        for (var i = 0; i < currentMessages.length; i++) {
            var msg = currentMessages[i]
            if (msg.component) {
                msg.component.destroy()
            }
        }
        currentMessages = []
        messageQueue = []
    }
}