# OpenCode 漏洞发现工作流系统

## 系统架构

```
用户入口 (entry.md)
    ↓
编排器 (orchestrator.md)
    ├─→ 初始化 (initialization.md)
    ├─→ Sink分析 (sink-analyzer.md)
    ├─→ Source追踪 (source-tracker.md)
    │      ├─→ CodeQL工具 (tool-codeql.md)
    │      └─→ LSP工具 (tool-lsp.md)
    ├─→ 上下文分析 (context-analyzer.md)
    └─→ 报告生成 (reporter.md)
```

## Agent列表

### 主Agent

| Agent | 文件 | 职责 |
|-------|------|------|
| **用户入口** | entry.md | 接收用户输入，验证参数，启动扫描 |
| **编排器** | orchestrator.md | 协调所有subagent，管理工作流程 |

### Subagent

| Agent | 文件 | 职责 |
|-------|------|------|
| **初始化** | initialization.md | 扫描项目，识别源代码文件 |
| **Sink分析** | sink-analyzer.md | 查找潜在漏洞的sink点 |
| **Source追踪** | source-tracker.md | 追踪数据流（source→sink） |
| **上下文分析** | context-analyzer.md | 验证漏洞真实性 |
| **报告生成** | reporter.md | 生成结构化报告 |

### 工具Agent

| Agent | 文件 | 职责 |
|-------|------|------|
| **CodeQL工具** | tool-codeql.md | CodeQL CLI调用接口 |
| **LSP工具** | tool-lsp.md | LSP调用接口 |

## 使用方法

### 基本用法

```bash
# 扫描指定目录
opencode scan /path/to/project

# 快速扫描模式
opencode scan /path/to/project --mode quick

# 完整扫描模式
opencode scan /path/to/project --mode full
```

### 扫描模式

| 模式 | 工具 | 耗时 | 准确性 |
|------|------|------|--------|
| quick | grep | 快 | 低 |
| standard | grep + LSP | 中 | 中 |
| full | grep + LSP + CodeQL | 慢 | 高 |

### 工作流程

```
用户输入
  ↓
1. entry.md 接收输入并验证
  ↓
2. orchestrator.md 协调执行
  ↓
3. initialization.md 初始化项目
  ↓
4. sink-analyzer.md 查找sink点
  ↓
5. source-tracker.md 追踪数据流（使用CodeQL和LSP工具）
  ↓
6. context-analyzer.md 验证漏洞
  ↓
7. reporter.md 生成报告
  ↓
8. entry.md 显示结果
```

## 目录结构

```
Lousix_code/.opencode/
├── agents/                          # Agent定义
│   ├── entry.md                     # 用户入口
│   ├── orchestrator.md              # 编排器
│   ├── initialization.md            # 项目初始化
│   ├── sink-analyzer.md             # Sink点分析
│   ├── source-tracker.md            # Source追踪
│   ├── context-analyzer.md          # 上下文分析
│   ├── reporter.md                  # 报告生成
│   ├── tool-codeql.md               # CodeQL工具
│   └── tool-lsp.md                  # LSP工具
├── workflows/                       # 工作流配置
│   └── vulnerability-discovery.yaml
├── reports/                         # 生成的报告
│   ├── project_info.json
│   ├── sink_points.json
│   ├── dataflow_paths.json
│   ├── verified_vulnerabilities.json
│   ├── vulnerability_report.md
│   └── vulnerability_report.json
└── README.md
```

## Agent调用关系

### Orchestrator调用Subagent

```
orchestrator.md (primary)
    ├─→ task(initialization)
    ├─→ task(sink-analyzer)
    ├─→ task(source-tracker)
    │     ├─→ 使用 tool-codeql.md
    │     └─→ 使用 tool-lsp.md
    ├─→ task(context-analyzer)
    └─→ task(reporter)
```

### Entry调用Orchestrator

```
entry.md (primary)
    ├─→ 接收用户输入
    ├─→ 验证参数
    └─→ task(orchestrator)
```

## 工具化设计

### CodeQL工具 (tool-codeql.md)

提供的功能：
1. 创建CodeQL数据库
2. 运行自定义查询
3. 运行内置查询套件
4. 解码查询结果
5. 查询模板库

调用方式：
```bash
# 创建数据库
codeql database create my-db --language=python --source-root=/path/to/project

# 运行查询
codeql query run --database=my-db query.ql --output=results.bqrs

# 解码结果
codeql bqrs decode --format=json --output=results.json results.bqrs
```

### LSP工具 (tool-lsp.md)

提供的功能：
1. 查找符号定义
2. 查找所有引用
3. 获取悬停信息
4. 获取文档符号
5. 跨文件调用追踪

调用方式：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "textDocument/definition",
  "params": {
    "textDocument": {"uri": "file:///path/to/file.py"},
    "position": {"line": 42, "character": 10}
  }
}
```

## 数据流

### 输入数据

```
用户输入:
  - project_path: /path/to/project
  - mode: full/standard/quick
  - config: (可选)
```

### 中间数据

```
project_info.json:
  - project_name
  - total_files
  - languages
  - high_risk_files

sink_points.json:
  - sink_id
  - file_path
  - line_number
  - sink_type
  - severity

dataflow_paths.json:
  - path_id
  - source (file, line, code)
  - sink (file, line, code)
  - data_flow (中间节点)

verified_vulnerabilities.json:
  - vulnerability_id
  - type
  - severity
  - confidence
  - source→sink路径
```

### 输出数据

```
vulnerability_report.md:
  - 执行摘要
  - 漏洞详情
  - 统计分析
  - 修复建议

vulnerability_report.json:
  - 结构化漏洞数据
  - 用于API集成
```

## 配置系统

### 默认配置

```yaml
scan:
  default_mode: full

tools:
  grep: {enabled: true}
  lsp: {enabled: true}
  codeql: {enabled: true}

exclude_dirs:
  - node_modules
  - .git
  - test
```

### 自定义配置

```bash
# 指定配置文件
opencode scan /path/to/project --config /path/to/config.yaml
```

## 支持的语言

| 语言 | CodeQL | LSP | 工具链 |
|------|--------|-----|--------|
| Python | ✅ | ✅ | pylsp |
| JavaScript | ✅ | ✅ | typescript-language-server |
| TypeScript | ✅ | ✅ | typescript-language-server |
| Java | ✅ | ✅ | jdt-language-server |
| C/C++ | ✅ | ✅ | clangd |
| Go | ✅ | ✅ | gopls |

## 漏洞类型

### Python

| 类型 | CWE | 严重性 |
|------|-----|--------|
| 命令注入 | CWE-78 | Critical |
| SQL注入 | CWE-89 | High |
| 路径遍历 | CWE-22 | High |
| 反序列化 | CWE-502 | High |
| XSS | CWE-79 | Medium |

### JavaScript/TypeScript

| 类型 | CWE | 严重性 |
|------|-----|--------|
| XSS | CWE-79 | High |
| 命令注入 | CWE-78 | Critical |
| 原型污染 | CWE-1321 | High |
| 路径遍历 | CWE-22 | High |

### Java

| 类型 | CWE | 严重性 |
|------|-----|--------|
| SQL注入 | CWE-89 | High |
| 命令注入 | CWE-78 | Critical |
| 路径遍历 | CWE-22 | High |
| 反序列化 | CWE-502 | High |

## 报告示例

### 执行摘要

```
═══════════════════════════════════════════════════════════════
                    扫描完成
═══════════════════════════════════════════════════════════════

项目: my-app
扫描时间: 2026-01-27 10:00:00
总耗时: 120秒

扫描统计:
  扫描文件: 500
  发现Sink点: 50
  数据流路径: 20
  验证漏洞: 15

风险分布:
  🔴 Critical: 2
  🟠 High: 5
  🟡 Medium: 5
  🟢 Low: 3

报告位置:
  📄 Markdown: .opencode/reports/vulnerability_report.md
  📊 JSON: .opencode/reports/vulnerability_report.json

═══════════════════════════════════════════════════════════════
```

### 漏洞详情

```markdown
#### 1. 命令注入 - app/utils.py:89

**漏洞ID**: VULN-001
**CWE**: CWE-78
**置信度**: 95%
**影响**: 远程代码执行

**数据流路径 (Source → Sink)**:

| 步骤 | 文件 | 行号 | 代码 | 说明 |
|------|------|------|------|------|
| 1. [SOURCE] | app/views.py | 45 | `user_input = request.form.get('cmd')` | 接收用户输入 |
| 2. | app/views.py | 48 | `execute_command(user_input)` | 函数调用 |
| 3. | app/utils.py | 85 | `def execute_command(user_input):` | 函数定义 |
| 4. [SINK] | app/utils.py | 89 | `os.system(user_input)` | 危险函数 |

**修复建议**:
```python
# 使用subprocess模块
import subprocess

result = subprocess.run(
    ["ls", user_input],
    capture_output=True,
    text=True
)
```
```

## 扩展性

### 添加新的漏洞类型

1. 在`sink-analyzer.md`中添加新的危险函数模式
2. 在`tool-codeql.md`中添加新的查询模板
3. 在`context-analyzer.md`中添加验证规则

### 支持新的语言

1. 添加语言的LSP服务器配置
2. 创建语言的CodeQL查询模板
3. 定义语言的危险函数列表

### 添加新的工具

1. 创建新的tool agent（如tool-ast.md）
2. 在orchestrator中集成新工具
3. 更新扫描模式配置

## 注意事项

1. **CodeQL安装**: 完整扫描需要安装CodeQL CLI
2. **LSP服务器**: 标准和完整扫描需要安装对应语言的LSP服务器
3. **磁盘空间**: CodeQL数据库创建需要足够空间
4. **超时设置**: 大型项目可能需要调整超时时间
5. **内存使用**: 完整扫描需要足够的内存

## 故障排除

### CodeQL未找到

```bash
# 安装CodeQL
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH=$PATH:$PWD/codeql
```

### LSP服务器未启动

```bash
# 安装PyLSP
pip install python-lsp-server

# 安装TypeScript Language Server
npm install -g typescript-language-server
```

### 扫描卡住

```bash
# 增加超时时间
opencode scan /path/to/project --timeout 1200

# 使用快速模式
opencode scan /path/to/project --mode quick
```

## 下一步

1. ✅ 已创建完整的Agent系统（基于OpenCode Markdown格式）
2. ✅ 已实现编排器和工具化
3. ⚠️ 需要在OpenCode环境中测试
4. ⚠️ 需要根据实际运行情况调整

## 相关文档

- `agents/entry.md` - 用户入口Agent
- `agents/orchestrator.md` - 编排器Agent
- `agents/initialization.md` - 初始化Agent
- `agents/sink-analyzer.md` - Sink分析Agent
- `agents/source-tracker.md` - Source追踪Agent
- `agents/context-analyzer.md` - 上下文分析Agent
- `agents/reporter.md` - 报告生成Agent
- `agents/tool-codeql.md` - CodeQL工具Agent
- `agents/tool-lsp.md` - LSP工具Agent

## 总结

已成功创建基于OpenCode Agent系统的漏洞发现工作流：

✅ **架构设计**:
- 主Agent：entry.md（用户入口）、orchestrator.md（编排器）
- Subagent：5个功能Agent
- 工具Agent：2个工具化Agent

✅ **工具化**:
- CodeQL工具：提供模板化查询接口
- LSP工具：提供符号追踪接口
- 所有工具都使用bash命令模板化

✅ **工作流程**:
- 3种扫描模式（quick/standard/full）
- 完整的5步分析流程
- 结构化的数据流

✅ **扩展性**:
- 模块化设计
- 易于添加新漏洞类型
- 易于支持新语言
- 易于添加新工具

系统已准备就绪，可以在OpenCode环境中使用！
