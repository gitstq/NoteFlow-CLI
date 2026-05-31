# 🧠 NoteFlow-CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-green.svg)]()

**Lightweight Terminal Intelligent Note & Knowledge Management Engine**

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english) | [日本語](#日本語)

---

## English

### 🎉 Introduction

**NoteFlow-CLI** is a lightweight, zero-dependency terminal note management tool designed specifically for developers. It provides intelligent note organization with full-text search, Git integration, and a beautiful TUI dashboard.

**Why NoteFlow-CLI?**
- 🔒 **Privacy First**: All data stored locally, no cloud required
- ⚡ **Zero Dependencies**: Pure Python implementation, no external packages needed
- 🔍 **Smart Search**: TF-IDF powered full-text search with relevance scoring
- 🔗 **Git Integration**: Automatically link notes to commits and branches
- 📊 **TUI Dashboard**: Interactive terminal interface with keyboard navigation
- 🏷️ **Smart Tags**: Flexible tagging system with categories
- 📦 **Multi-Format Export**: Export to Markdown, JSON, and more

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📝 **Note Management** | Create, edit, delete, archive notes with Markdown support |
| 🔍 **Full-Text Search** | TF-IDF powered search with boolean queries |
| 📁 **Categories** | Organize notes into hierarchical categories |
| 🏷️ **Tags** | Flexible tagging system for note classification |
| 📌 **Pin Notes** | Pin important notes for quick access |
| 🔗 **Git Integration** | Auto-link notes to current branch/commit |
| 📊 **TUI Dashboard** | Interactive terminal UI with keyboard navigation |
| 📤 **Import/Export** | JSON and Markdown export/import |
| 📈 **Statistics** | Track your note-taking habits |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- No external dependencies required!

#### Installation

```bash
# Install from PyPI (recommended)
pip install noteflow-cli

# Or install from source
git clone https://github.com/gitstq/NoteFlow-CLI.git
cd NoteFlow-CLI
pip install -e .
```

#### Basic Usage

```bash
# Create a new note
noteflow new "My First Note" -c "This is the content"

# List all notes
noteflow list

# Search notes
noteflow search "python"

# Show note details
noteflow show <note_id>

# Create a quick note
noteflow quick "Quick thought to save"

# View statistics
noteflow stats
```

### 📖 Detailed Usage Guide

#### Creating Notes

```bash
# Basic note
noteflow new "Meeting Notes" -c "Discussed project timeline"

# With tags
noteflow new "Bug Report" -c "Description..." -t bug,urgent

# With priority
noteflow new "Critical Issue" -c "..." --priority critical

# Read content from file
noteflow new "Documentation" -f ./docs.md

# Read from stdin
echo "Quick note content" | noteflow new "Title" --stdin
```

#### Managing Notes

```bash
# List notes with filters
noteflow list --status draft
noteflow list --tags work,important
noteflow list --pinned

# Edit a note
noteflow edit <note_id> --title "New Title"
noteflow edit <note_id> --tags new,tags

# Pin/Unpin notes
noteflow pin <note_id>
noteflow pin <note_id> --unpin

# Archive notes
noteflow archive <note_id>
noteflow archive <note_id> --restore

# Delete notes
noteflow delete <note_id> -f  # Force delete without confirmation
```

#### Searching

```bash
# Basic search
noteflow search "python tutorial"

# Search with filters
noteflow search "api" --tags documentation
noteflow search "bug" --status draft

# Limit results
noteflow search "project" --limit 20
```

#### Categories and Tags

```bash
# List categories
noteflow category --list

# Create category
noteflow category --create "Work" --icon "💼"

# Delete category
noteflow category --delete <category_id>

# List tags
noteflow tag --list

# Delete tag
noteflow tag --delete "old-tag"
```

#### Import/Export

```bash
# Export to JSON
noteflow export notes.json --format json

# Export to Markdown
noteflow export ./markdown_notes --format markdown

# Import from JSON
noteflow import notes.json
```

### 💡 Design Philosophy

NoteFlow-CLI was built with these principles in mind:

1. **Simplicity**: Zero external dependencies means easy installation and reliable operation
2. **Privacy**: Your notes stay on your machine - no cloud, no tracking
3. **Developer-Friendly**: Git integration, Markdown support, CLI-first design
4. **Performance**: Lightweight indexing for fast search even with thousands of notes

### 📦 Build & Deployment

```bash
# Build package
pip install build
python -m build

# Run tests
pip install pytest
pytest tests/

# Type checking
pip install mypy
mypy noteflow/
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 简体中文

### 🎉 项目介绍

**NoteFlow-CLI** 是一款专为开发者设计的轻量级、零依赖终端笔记管理工具。提供智能笔记组织、全文搜索、Git集成和美观的TUI仪表板。

**核心价值：**
- 🔒 **隐私优先**：所有数据本地存储，无需云端
- ⚡ **零依赖**：纯Python实现，无需安装任何外部包
- 🔍 **智能搜索**：基于TF-IDF的全文搜索，支持相关性排序
- 🔗 **Git集成**：自动关联笔记与Git提交和分支
- 📊 **TUI仪表板**：交互式终端界面，键盘导航
- 🏷️ **智能标签**：灵活的标签分类系统

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 📝 **笔记管理** | 创建、编辑、删除、归档笔记，支持Markdown |
| 🔍 **全文搜索** | TF-IDF驱动的搜索，支持布尔查询 |
| 📁 **分类管理** | 层级分类组织笔记 |
| 🏷️ **标签系统** | 灵活的标签分类 |
| 📌 **置顶功能** | 重要笔记快速访问 |
| 🔗 **Git集成** | 自动关联当前分支/提交 |
| 📊 **TUI界面** | 交互式终端界面 |
| 📤 **导入导出** | JSON和Markdown格式支持 |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- 无需任何外部依赖！

#### 安装

```bash
# 从PyPI安装（推荐）
pip install noteflow-cli

# 或从源码安装
git clone https://github.com/gitstq/NoteFlow-CLI.git
cd NoteFlow-CLI
pip install -e .
```

#### 基本使用

```bash
# 创建新笔记
noteflow new "我的第一篇笔记" -c "这是内容"

# 列出所有笔记
noteflow list

# 搜索笔记
noteflow search "关键词"

# 查看笔记详情
noteflow show <笔记ID>

# 创建快速笔记
noteflow quick "快速记录的想法"

# 查看统计
noteflow stats
```

### 📖 详细使用指南

#### 创建笔记

```bash
# 基本笔记
noteflow new "会议记录" -c "讨论了项目进度"

# 带标签
noteflow new "Bug报告" -c "描述..." -t bug,紧急

# 设置优先级
noteflow new "重要问题" -c "..." --priority critical

# 从文件读取内容
noteflow new "文档" -f ./docs.md

# 从标准输入读取
echo "快速笔记内容" | noteflow new "标题" --stdin
```

#### 管理笔记

```bash
# 带筛选条件列出
noteflow list --status draft
noteflow list --tags 工作,重要
noteflow list --pinned

# 编辑笔记
noteflow edit <笔记ID> --title "新标题"
noteflow edit <笔记ID> --tags 新标签

# 置顶/取消置顶
noteflow pin <笔记ID>
noteflow pin <笔记ID> --unpin

# 归档笔记
noteflow archive <笔记ID>
noteflow archive <笔记ID> --restore

# 删除笔记
noteflow delete <笔记ID> -f  # 强制删除无需确认
```

### 💡 设计思路

NoteFlow-CLI 的设计理念：

1. **简洁**：零外部依赖，安装简单，运行可靠
2. **隐私**：笔记保存在本地，无云端，无追踪
3. **开发者友好**：Git集成、Markdown支持、CLI优先设计
4. **性能**：轻量级索引，即使数千笔记也能快速搜索

### 📦 打包与部署

```bash
# 构建包
pip install build
python -m build

# 运行测试
pip install pytest
pytest tests/

# 类型检查
pip install mypy
mypy noteflow/
```

### 🤝 贡献指南

欢迎贡献代码！请随时提交Pull Request。

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

## 繁體中文

### 🎉 專案介紹

**NoteFlow-CLI** 是一款專為開發者設計的輕量級、零依賴終端筆記管理工具。提供智慧筆記組織、全文搜尋、Git整合和美觀的TUI儀表板。

**核心價值：**
- 🔒 **隱私優先**：所有資料本地儲存，無需雲端
- ⚡ **零依賴**：純Python實現，無需安裝任何外部套件
- 🔍 **智慧搜尋**：基於TF-IDF的全文搜尋，支援相關性排序
- 🔗 **Git整合**：自動關聯筆記與Git提交和分支
- 📊 **TUI儀表板**：互動式終端介面，鍵盤導航

### 🚀 快速開始

#### 環境要求
- Python 3.8 或更高版本
- 無需任何外部依賴！

#### 安裝

```bash
# 從PyPI安裝（推薦）
pip install noteflow-cli

# 或從原始碼安裝
git clone https://github.com/gitstq/NoteFlow-CLI.git
cd NoteFlow-CLI
pip install -e .
```

#### 基本使用

```bash
# 建立新筆記
noteflow new "我的第一篇筆記" -c "這是內容"

# 列出所有筆記
noteflow list

# 搜尋筆記
noteflow search "關鍵詞"

# 查看筆記詳情
noteflow show <筆記ID>
```

### 📄 開源協議

本專案採用 MIT 協議開源。

---

## 日本語

### 🎉 プロジェクト紹介

**NoteFlow-CLI** は開発者向けに設計された軽量で依存関係のないターミナルノート管理ツールです。

**主な特徴：**
- 🔒 **プライバシー重視**：すべてのデータはローカルに保存
- ⚡ **ゼロ依存**：純粋なPython実装、外部パッケージ不要
- 🔍 **スマート検索**：TF-IDFベースの全文検索
- 🔗 **Git統合**：コミットとブランチに自動リンク

### 🚀 クイックスタート

```bash
# インストール
pip install noteflow-cli

# 新しいノートを作成
noteflow new "私の最初のノート" -c "コンテンツ"

# ノート一覧
noteflow list

# 検索
noteflow search "キーワード"
```

### 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

<p align="center">
  Made with ❤️ by NoteFlow Team
</p>
