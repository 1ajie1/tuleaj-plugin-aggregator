import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

Rectangle {
    id: settingsTheme
    width: parent.width
    height: themeColumnLayout.implicitHeight + 24  // 内容高度 + 边距
    color: "#f8f9fa"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    
    ColumnLayout {
        id: themeColumnLayout
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 24  // 增加左右边距
        anchors.rightMargin: 24
        anchors.topMargin: 12
        anchors.bottomMargin: 12
        spacing: 12  // 减少间距
        
        RowLayout {
            spacing: 8  // 添加间距
            
            Text {
                text: "主题模式:"
                font.pixelSize: 14
                color: "#333333"
                Layout.preferredWidth: 80
            }
            
            ComboBox {
                id: themeComboBox
                model: ["light", "dark", "auto"]
                currentIndex: {
                    if (configBridge) {
                        switch(configBridge.theme) {
                            case "light": return 0
                            case "dark": return 1
                            case "auto": return 2
                            default: return 0
                        }
                    }
                    return 0
                }
                Layout.fillWidth: true
                
                onCurrentIndexChanged: {
                    if (configBridge) {
                        var themes = ["light", "dark", "auto"]
                        if (currentIndex >= 0 && currentIndex < themes.length) {
                            configBridge.setTheme(themes[currentIndex])
                        }
                    }
                }
            }
        }
    }
}
