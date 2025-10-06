import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#ffffff"
    
    // 属性
    property string currentPluginName: ""
    property string currentPluginDescription: ""
    
    // 信号定义
    signal settingsRequested()
    signal addPluginRequested()
    
    // 函数：加载插件文档
    function loadPluginDocument(pluginName) {
        currentPluginName = pluginName
        currentPluginDescription = getPluginDescription(pluginName)
        markdownViewer.text = getPluginDocument(pluginName)
    }
    
    // 获取插件描述
    function getPluginDescription(pluginName) {
        switch(pluginName) {
            case "系统监控":
                return "实时系统监控工具, 显示CPU、内存使用情况和系统状态"
            case "Chrome Extension Tools":
                return "Chrome浏览器扩展开发和调试工具, 提供实时监控和性能分析"
            case "Figma Plugin SDK":
                return "Figma插件开发SDK, 包含完整的API文档和示例代码"
            case "Data Visualization":
                return "数据可视化工具集, 支持多种图表类型和交互式分析"
            case "Package Manager":
                return "智能包管理器, 自动处理依赖关系和版本冲突"
            default:
                return "插件描述"
        }
    }
    
    // 获取插件文档内容
    function getPluginDocument(pluginName) {
        switch(pluginName) {
            case "系统监控":
                var doc = "# 系统监控插件\n\n## 功能概述\n\n"
                doc += "系统监控插件是一个实时系统资源监控工具，提供直观的CPU和内存使用情况显示。\n\n"
                doc += "## 主要功能\n\n### CPU 监控\n"
                doc += "- **实时CPU使用率**: 显示当前CPU使用百分比\n"
                doc += "- **动态进度条**: 直观的可视化显示\n"
                doc += "- **实时更新**: 持续监控CPU状态变化\n\n"
                doc += "### 内存监控\n"
                doc += "- **内存使用率**: 显示当前内存使用百分比\n"
                doc += "- **总内存信息**: 显示系统总内存容量\n"
                doc += "- **已用内存**: 显示当前已使用的内存量\n"
                doc += "- **可视化显示**: 通过进度条直观展示内存使用情况\n\n"
                doc += "## 技术特性\n\n"
                doc += "- **轻量级**: 占用系统资源极少\n"
                doc += "- **实时性**: 毫秒级数据更新\n"
                doc += "- **跨平台**: 支持Windows、macOS、Linux\n"
                doc += "- **用户友好**: 简洁直观的界面设计\n\n"
                doc += "## 使用方法\n\n"
                doc += "1. 在插件列表中点击\"启动\"按钮\n"
                doc += "2. 系统监控窗口将自动打开\n"
                doc += "3. 实时查看CPU和内存使用情况\n"
                doc += "4. 点击窗口关闭按钮停止监控\n\n"
                doc += "## 系统要求\n\n"
                doc += "- Python 3.11+\n"
                doc += "- PySide6\n"
                doc += "- psutil (系统信息获取)\n\n"
                doc += "## 注意事项\n\n"
                doc += "- 监控数据每100毫秒更新一次\n"
                doc += "- 关闭监控窗口不会停止插件运行\n"
                doc += "- 需要在主应用中点击\"停止\"按钮完全停止插件"
                return doc
            
            case "Figma Plugin SDK":
                return "# 构建强大的Figma插件\n\n## SDK概述\n\nFigma Plugin SDK 是一个强大的开发工具包，为开发者提供了创建功能丰富、交互性强的Figma插件的完整解决方案。\n\n## 核心功能\n\n### 节点操作\n- **选择节点**: 精确选择和操作Figma设计元素\n- **创建节点**: 动态创建各种UI组件\n- **修改属性**: 实时修改节点属性和样式\n\n### API集成\n- **RESTful API**: 完整的REST API接口\n- **WebSocket支持**: 实时数据同步\n- **认证系统**: 安全的用户认证机制\n\n### 开发工具\n- **调试器**: 内置调试工具，支持断点调试\n- **性能监控**: 实时性能分析和优化建议\n- **代码提示**: 智能代码补全和语法检查\n\n## 快速开始\n\n1. 安装SDK\n2. 创建新项目\n3. 配置开发环境\n4. 开始编码\n\n## 示例代码\n\n```javascript\n// 创建新节点\nconst newNode = figma.createRectangle();\nnewNode.resize(100, 100);\nnewNode.fills = [{type: 'SOLID', color: {r: 1, g: 0, b: 0}}];\n```\n\n## 最佳实践\n\n- 遵循Figma设计规范\n- 优化插件性能\n- 提供良好的用户体验\n- 完善的错误处理机制"
            
            case "Chrome Extension Tools":
                return "# Chrome Extension Tools\n\n## 功能特性\n\nChrome Extension Tools 是一套完整的Chrome浏览器扩展开发工具集。\n\n### 开发工具\n- 实时调试\n- 性能分析\n- 代码审查\n\n### 监控功能\n- 扩展性能监控\n- 用户行为分析\n- 错误日志收集\n\n## 使用方法\n\n1. 安装工具\n2. 配置项目\n3. 开始开发\n\n## 技术栈\n\n- JavaScript ES6+\n- Chrome Extension API\n- Webpack\n- Babel"
            
            case "Data Visualization":
                return "# Data Visualization\n\n## 概述\n\n数据可视化工具集，提供丰富的图表类型和交互式分析功能。\n\n## 支持的图表类型\n\n- 柱状图\n- 折线图\n- 饼图\n- 散点图\n- 热力图\n\n## 特性\n\n- 响应式设计\n- 交互式操作\n- 数据导出\n- 自定义主题"
            
            case "Package Manager":
                return "# Package Manager\n\n## 智能包管理\n\n智能包管理器，自动处理依赖关系和版本冲突。\n\n## 主要功能\n\n- 依赖解析\n- 版本管理\n- 冲突检测\n- 自动更新\n\n## 支持格式\n\n- npm\n- yarn\n- pnpm\n- pip"
            
            default:
                return "# 请选择一个插件查看文档\n\n从左侧列表中选择一个插件来查看其详细文档。\n\n## 使用说明\n\n1. 在左侧插件列表中选择您感兴趣的插件\n2. 查看插件的详细文档和说明\n3. 使用启动/停止按钮控制插件状态\n\n## 插件状态\n\n- **运行中**: 插件正在正常运行\n- **已停止**: 插件已停止运行\n- **错误**: 插件运行出现错误"
        }
    }
    
    // 主布局
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        // 主要内容区域
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ColumnLayout {
                width: parent.width
                spacing: 24
                anchors.margins: 24
                
                // 顶部标题区域
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    
                    // 插件主标题
                    Text {
                        text: currentPluginName || "插件聚合器"
                        font.pixelSize: 28
                        font.bold: true
                        color: "#333333"
                        Layout.fillWidth: true
                    }
                    
                    // 插件副标题
                    Text {
                        text: currentPluginDescription || "请选择一个插件查看文档"
                        font.pixelSize: 16
                        color: "#666666"
                        Layout.fillWidth: true
                    }
                }
                
                // 文档内容区域
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        Text {
                            id: markdownViewer
                            width: parent.width
                            text: "请选择一个插件查看文档"
                            font.pixelSize: 14
                            color: "#333333"
                            wrapMode: Text.WordWrap
                            textFormat: Text.RichText
                            lineHeight: 1.6
                            
                            // 简单的Markdown渲染
                            onTextChanged: {
                                // 这里可以实现Markdown渲染逻辑
                                // 目前使用简单的文本显示
                            }
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
                            root.settingsRequested()
                        }
                        
                        onEntered: {
                            settingsButton.color = "#e8e8e8"
                            settingsButton.border.color = "#d0d0d0"
                        }
                        
                        onExited: {
                            settingsButton.color = "#f5f5f5"
                            settingsButton.border.color = "#e0e0e0"
                        }
                        
                        onPressed: {
                            settingsButton.color = "#d0d0d0"
                            settingsButton.border.color = "#c0c0c0"
                        }
                        
                        onReleased: {
                            settingsButton.color = "#e8e8e8"
                            settingsButton.border.color = "#d0d0d0"
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
                            root.addPluginRequested()
                        }
                        
                        onEntered: {
                            addPluginButton.color = "#45a049"
                        }
                        
                        onExited: {
                            addPluginButton.color = "#4CAF50"
                        }
                        
                        onPressed: {
                            addPluginButton.color = "#3d8b40"
                        }
                        
                        onReleased: {
                            addPluginButton.color = "#45a049"
                        }
                    }
                }
            }
        }
    }
}
