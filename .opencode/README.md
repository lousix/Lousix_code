# OpenCode 漏洞发现工作流

自动化深度分析代码中的潜在漏洞，使用CodeQL和LSP追踪数据流从source到sink的完整路径。

## 功能特点

- 🔍 **深度分析**: 逐步分析每个文件，查找潜在漏洞的sink点
- 🔗 **数据流追踪**: 基于sink点，使用CodeQL/LSP追踪source点和完整数据通路
- 📊 **上下文分析**: 提取漏洞上下文，验证漏洞真实性，减少误报
- 📝 **结构化报告**: 生成详细的漏洞报告，包含source→sink通路、修复建议等

## 工作流架构

```
┌─────────────────────────────────────────────────────────────┐
│              OpenCode Vulnerability Discovery               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 项目初始化     │    │  Sink点分析    │    │ Source追踪    │
│ Agent         │───▶│ Agent         │───▶│ Agent         │
│               │    │               │    │ (CodeQL+LSP)  │
└───────────────┘    └───────────────┘    └───────────────┘
                                                │
                                                ▼
                                      ┌───────────────┐
                                      │ 上下文分析     │
                                      │ Agent         │
                                      └───────────────┘
                                                │
                                                ▼
                                      ┌───────────────┐
                                      │ 报告生成       │
                                      │ Agent         │
                                      └───────────────┘
```

## 支持的语言

- Python
- JavaScript / TypeScript
- Java
- C / C++
- Go
- Ruby
- PHP

## 支持的漏洞类型

### 高危漏洞
- 命令注入 (CWE-78)
- SQL注入 (CWE-89)
- 反序列化漏洞 (CWE-502)

### 中危漏洞
- 路径遍历 (CWE-22)
- 跨站脚本 (XSS) (CWE-79)
- 服务端请求伪造 (SSRF) (CWE-918)

### 其他漏洞
- 格式化字符串 (CWE-134)
- 原型污染 (CWE-1321)
- 缓冲区溢出 (CWE-120)

## 目录结构

```
Lousix_code/
├── .opencode/
│   ├── agents/              # Agent定义文件
│   │   ├── initialization.md
│   │   ├── sink-analyzer.md
│   │   ├── source-tracker.md
│   │   ├── context-analyzer.md
│   │   └── reporter.md
│   ├── workflows/           # 工作流配置
│   │   └── vulnerability-discovery.yaml
│   ├── reports/             # 生成的报告
│   │   ├── vulnerability_report.md
│   │   ├── vulnerability_report.json
│   │   ├── project_info.json
│   │   ├── sink_points.json
│   │   ├── dataflow_paths.json
│   │   └── verified_vulnerabilities.json
│   └── workflow.py          # 主执行脚本
└── [源代码文件]
```

## 安装依赖

### 1. Python依赖

```bash
pip install -r requirements.txt
```

### 2. CodeQL安装 (可选但推荐)

```bash
# 从GitHub下载最新版本
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip

# 解压
unzip codeql-linux64.zip

# 添加到PATH
export PATH=$PATH:/path/to/codeql
```

### 3. LSP服务器

根据使用的语言安装对应的LSP服务器：

- Python: `pip install python-lsp-server`
- JavaScript/TypeScript: `npm install -g typescript-language-server`
- Java: 安装Eclipse JDT Language Server
- Go: `go install golang.org/x/tools/gopls@latest`

## 使用方法

### 基本使用

```bash
# 在Lousix_code目录下运行
cd .opencode
python workflow.py

# 或者指定其他项目路径
python workflow.py /path/to/other/project
```

### 查看报告

```bash
# 查看Markdown报告
cat reports/vulnerability_report.md

# 查看JSON格式报告
cat reports/vulnerability_report.json | jq .
```

### 查看中间结果

```bash
# 项目信息
cat reports/project_info.json

# Sink点列表
cat reports/sink_points.json

# 数据流路径
cat reports/dataflow_paths.json

# 验证后的漏洞
cat reports/verified_vulnerabilities.json
```

## 工作流步骤详解

### 1. 项目初始化

- 扫描项目目录，识别所有源代码文件
- 检测项目使用的编程语言
- 排除测试文件、生成代码、第三方库
- 生成项目信息JSON

**输出**: `project_info.json`

### 2. Sink点分析

- 逐步分析每个文件
- 识别潜在的漏洞sink点（危险函数调用）
- 记录sink点的上下文信息
- 按严重性标记优先级

**输出**: `sink_points.json`

### 3. Source追踪

- 基于已识别的sink点
- 使用CodeQL进行精确的数据流分析
- 使用LSP进行符号追踪
- 构建从source到sink的完整路径

**输出**: `dataflow_paths.json`

### 4. 上下文分析

- 提取数据流的完整上下文
- 检查输入校验和净化逻辑
- 分析控制流可达性
- 验证漏洞真实性，减少误报

**输出**: `verified_vulnerabilities.json`

### 5. 报告生成

- 生成Markdown格式的详细报告
- 包含漏洞统计、详细信息、修复建议
- 同时生成JSON格式的结构化数据

**输出**: `vulnerability_report.md`, `vulnerability_report.json`

## 配置选项

编辑 `.opencode/workflows/vulnerability-discovery.yaml`:

```yaml
config:
  use_codeql: true      # 是否使用CodeQL
  use_lsp: true         # 是否使用LSP
  max_depth: 5          # 最大追踪深度
  timeout: 3600         # 超时时间（秒）
```

## 输出示例

### 报告摘要

```
执行摘要
项目名称: my-project
扫描时间: 2026-01-27 10:00:00
扫描工具: OpenCode Vulnerability Scanner
分析方法: CodeQL + LSP + 静态分析
扫描文件数: 150

风险概览
严重性    数量  占比
🔴 Critical    3    12%
🟠 High        8    32%
🟡 Medium     10    40%
🟢 Low         4    16%
总计         25   100%
```

### 漏洞详情示例

```
#### 1. 命令注入 - app/views.py:89

漏洞ID: VULN-001
CWE: CWE-78
置信度: 95%
影响: 远程代码执行

数据流路径 (Source → Sink):

| 步骤 | 文件             | 行号 | 代码                              | 说明         |
|------|------------------|------|-----------------------------------|--------------|
| 1. [SOURCE] | app/views.py    | 45   | `user_input = request.form.get('cmd')` | 接收用户输入 |
| 2.    | app/utils.py     | 89   | `os.system(user_input)`          | 命令执行     |

修复建议:
```python
# 使用subprocess模块
import subprocess

result = subprocess.run(
    ["ls", user_input],  # 使用列表形式，防止注入
    capture_output=True,
    text=True
)
```
```

## 性能优化

- **并行处理**: 多个文件可以并行分析
- **缓存**: 缓存LSP查询结果，避免重复分析
- **优先级排序**: 优先分析高风险文件
- **增量扫描**: 支持只扫描变更的文件

## 限制和注意事项

1. **CodeQL要求**: CodeQL需要单独安装，但不是必需的
2. **LSP支持**: 需要安装对应语言的LSP服务器
3. **误报率**: 虽然有上下文分析，但仍可能有少量误报
4. **大型项目**: 对于大型项目（>1000个文件），建议分批扫描

## 故障排除

### CodeQL未找到

```bash
# 检查CodeQL安装
which codeql

# 如果未找到，手动添加到PATH
export PATH=$PATH:/path/to/codeql
```

### LSP服务器未启动

```bash
# 检查LSP服务器
which pyls  # Python LSP

# 如果未安装
pip install python-lsp-server
```

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- Issue: https://github.com/anomalyco/opencode/issues
- 文档: https://opencode.ai
