import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ConfigBridge 1.0

Rectangle {
    id: settingsPlugin
    width: parent.width
    height: pluginColumnLayout.implicitHeight + 24  // 内容高度 + 边距
    color: "#f8f9fa"
    radius: 8
    border.color: "#e0e0e0"
    border.width: 1
    
    ColumnLayout {
        id: pluginColumnLayout
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
            CheckBox {
                id: updateCheckBox
                text: "自动检查插件更新"
                checked: configBridge ? configBridge.autoScan : false
                
                onCheckedChanged: {
                    if (configBridge) {
                        configBridge.setAutoScan(checked)
                    }
                }
            }
        }
        
        RowLayout {
            CheckBox {
                id: debugModeCheckBox
                text: "启用调试模式"
                checked: configBridge ? configBridge.debugMode : false
                
                onCheckedChanged: {
                    if (configBridge) {
                        configBridge.setDebugMode(checked)
                    }
                }
            }
        }

        RowLayout {
            spacing: 8  // 添加间距
            
            Text {
                text: "插件超时时间:"
                font.pixelSize: 14
                color: "#333333"
                Layout.preferredWidth: 100
            }
            
            SpinBox {
                id: pluginTimeoutSpinBox
                from: 5
                to: 60
                value: configBridge ? configBridge.pluginTimeout : 30
                Layout.fillWidth: true
                
                onValueChanged: {
                    if (configBridge) {
                        configBridge.setPluginTimeout(value)
                    }
                }
            }
            
            Text {
                text: " 秒"
                font.pixelSize: 12
                color: "#666666"
                Layout.preferredWidth: 30
            }
        }
    }
}
