---
name: codeql
description: CodeQL查询执行工具，使用已有数据库和现成查询文件进行安全分析
license: MIT
compatibility: opencode
metadata:
  category: security
  languages: python javascript java cpp
  difficulty: intermediate
  audience: security-researchers
  tools: scripts/codeql-query.py
---

## What I do

I provide comprehensive guidance for running CodeQL queries using **existing databases** and **pre-written query files**:

### Primary Tool: `scripts/codeql-query.py`

- **Run single queries** - Execute existing `.ql` files or codeql dict against databases

### Core Assumptions

- **Database exists**: You have a ready-to-use CodeQL database
- **Queries are available**: Query files are located in `codeql-queries/` directory

## When to use me

Use this when you need to:

- Run existing CodeQL queries against a database
- Analyze security vulnerabilities using query suites
- Generate security reports from query results
- Compare results from multiple queries
- Prepare findings for manual review

## Prerequisites

### 1. Python Environment

**重要提示**: 在不同系统中，Python 命令可能不同：

- **Python 3.x**: 使用 `python3` 命令（推荐）
- **Python 2.x**: 使用 `python` 命令（已弃用）

检查系统中的 Python 版本：

```bash
# 检查 Python 3
python3 --version

# 如果 python3 不可用，尝试 python
python --version
```

**本 Skill 中的所有示例使用 `python3`，如果你的系统中使用 `python` 命令，请相应替换。**

### 2. CodeQL Database Available

假设你有一个现有的数据库，位于已知路径：

```
database/WebGoat/          # 示例数据库路径
database/PythonApp/         # 另一个示例
```

### 3. Query Files Directory

假设查询文件组织在 `codeql-queries/` 目录中：

```
codeql-queries/
├── test/
│   ├── cwe-022-path-traversal.ql
│   ├── cwe-078-command-injection.ql
│   └── cwe-089-sql-injection.ql
└── custom/
    └── business-logic-vulns.ql
```

### 4. Python Script Ready

`scripts/codeql-query.py` 脚本位于codeql agent skill 目录下的scripts/。

## Quick Start

### Example 1: 运行单个查询

```bash
# 运行查询
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output database/WebGoat/results/test/cwe-022-path-traversal.json
```

### Example 2: 运行查询套件

query参数输入是存放codeql查询语句的目录

```bash
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/ \
  --output database/WebGoat/results/test/test.json
```

### Example 3: 解密bqrs文件

query参数输入是存放codeql查询语句的目录

```bash
codeql bqrs decode database/WebGoat/results/test/cwe-089-sql-injection.bqrs --format=csv --output
=<file_path>.csv

codeql bqrs decode database/WebGoat/results/test/cwe-089-sql-injection.bqrs --format=json --output
=<file_path>.json
```
<!-- 
### Example 4: 查看结果

```bash
# 使用 jq 查看 JSON 结果
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '.results'

# 统计结果数量
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '.results | length'

# 查看查询结果具体内容
jq ".runs[0].invocations[0].toolExecutionNotifications" database/WebGoat/results/test/cwe-022-path-traversal.json
``` -->

## Python Script Usage

### 1. Run Single Query

**基本用法（直接形式）**:

```bash
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output database/WebGoat/results/test/cwe-022-path-traversal.json
```


**参数说明**:

- `--database`: CodeQL 数据库路径
- `--query`: `.ql` 查询文件路径
- `--output`: 输出 `.json` 文件路径

### 2. Run Query Suite

**安全套件示例**:

```bash
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/ \
  --output database/WebGoat/results/test/cwe-022-path-traversal.json
```


**参数说明**:

- `--database`: CodeQL 数据库路径
- `--query`: 查询文件目录路径
- `--output`: 输出 `.json` 文件路径

**内置安全套件**:
| 套件 | 语言 | 覆盖范围 |
|------|------|----------|
| `codeql-queries/test` | test | 测试项目 |


## Query File Examples

### 基于 `codeql-queries/` 目录结构

**注意**: 以下列出的查询文件都是现成的，直接使用即可，无需创建或修改。

### Security Queries (test/)

- `codeql-queries/test/cwe-022-path-traversal.ql` - Path Traversal (路径遍历)
- `codeql-queries/test/cwe-078-command-injection.ql` - Command Injection (命令注入)
- `codeql-queries/test/cwe-089-sql-injection.ql` - SQL Injection (SQL注入)
- `codeql-queries/test/cwe-079-xss.ql` - Cross-Site Scripting (XSS)
- `codeql-queries/test/cwe-502-deserialization.ql` - Deserialization (反序列化)

### Custom Queries (custom/)

- `codeql-queries/custom/business-logic-vulns.ql` - Business Logic Vulnerabilities (业务逻辑漏洞)
- `codeql-queries/custom/auth-issues.ql` - Authentication Issues (认证问题)
- `codeql-queries/custom/access-control.ql` - Access Control Issues (访问控制问题)

### Suites (suites/)

- `codeql-queries/suites/security-custom.yaml` - Custom Security Suite (自定义安全套件)

**使用示例**:

```bash
# 使用 test 目录下的查询
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output results/path-traversal.json

# 使用 custom 目录下的查询
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/custom/business-logic-vulns.ql \
  --output results/business-logic.json
```