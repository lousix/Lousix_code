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

- **Run single queries** - Execute existing `.ql` files against databases

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

`codeql-query.py` 脚本位于codeql agent skill 目录下的scripts/。

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

### Example 3: 查看结果

```bash
# 使用 jq 查看 JSON 结果
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '.results'

# 统计结果数量
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '.results | length'

# 查看查询结果具体内容
jq ".runs[0].invocations[0].toolExecutionNotifications" database/WebGoat/results/test/cwe-022-path-traversal.json
```

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
- `--output`: 输出 `.bqrs` 文件路径

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

## Complete Workflows

### Workflow 1: 单个查询分析

**目标**: 对特定漏洞类型进行深度分析

**步骤**:

```bash
# 步骤 1: 运行查询
python3 codeql-query.py \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output database/WebGoat/results/test/cwe-022-path-traversal.json

# 步骤 2: 查看结果摘要
echo "=== 结果摘要 ==="
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '{
  total: (.results | length),
  files: [.results[].locations[].physicalLocation.artifactLocation.uri] | unique | length
}'

# 步骤 3: 提取所有受影响的文件
echo "=== 受影响的文件 ==="
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq -r '.results[].locations[].physicalLocation.artifactLocation.uri' | sort | uniq

# 步骤 4: 查看具体漏洞位置
echo "=== 漏洞详情 ==="
cat database/WebGoat/results/test/cwe-022-path-traversal.json | jq '.results[] | {
  file: .locations[].physicalLocation.artifactLocation.uri,
  line: .locations[].physicalLocation.region.startLine,
  message: .message.text
}'
```

### Workflow 2: 批量查询执行

**目标**: 运行多个查询以获得全面的安全评估

**步骤**:

```bash
#!/bin/bash
# batch-scan.sh - 批量安全扫描脚本

DATABASE="database/WebGoat"
QUERY_DIR="codeql-queries/test"
RESULTS_DIR="results/scan-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$RESULTS_DIR"

echo "=== 开始批量安全扫描 ==="
echo "数据库: $DATABASE"
echo "查询目录: $QUERY_DIR"
echo "结果目录: $RESULTS_DIR"
echo ""

# 遍历所有查询文件
for query_file in "$QUERY_DIR"/*.ql; do
  if [ -f "$query_file" ]; then
    query_name=$(basename "$query_file" .ql)
    bqrs_file="$RESULTS_DIR/${query_name}.bqrs"
    json_file="$RESULTS_DIR/${query_name}.json"

    echo "运行查询: $query_name"

    # 运行查询
    python3 codeql-query.py \
      --database "$DATABASE" \
      --query "$query_file" \
      --output "$bqrs_file"

    # 解码为 JSON
    python3 codeql-query.py decode-bqrs \
      --input "$bqrs_file" \
      --format json \
      --output "$json_file"

    # 统计结果
    result_count=$(cat "$json_file" | jq '.results | length')
    echo "  发现漏洞: $result_count"
    echo ""
  fi
done

echo "=== 扫描完成 ==="
echo "结果保存在: $RESULTS_DIR"
```

**运行批量扫描**:

```bash
# 使脚本可执行
chmod +x batch-scan.sh

# 运行扫描
./batch-scan.sh

# 或直接在命令行执行
for query in codeql-queries/test/cwe-*.ql; do
  query_name=$(basename $query .ql)
  echo "Running $query_name..."

  python3 codeql-query.py \
    --database database/WebGoat \
    --query $query \
    --output results/test/$query_name.json
done
```

### Workflow 3: 多查询结果对比

**目标**: 比较不同查询的结果，识别高风险区域

**步骤**:

```bash
#!/bin/bash
# compare-results.sh - 查询结果对比脚本

RESULTS_DIR="results/test"

echo "=== 查询结果对比 ==="
echo ""

# 汇总所有查询的统计信息
echo "=== 汇总统计 ==="
for json_file in "$RESULTS_DIR"/*.json; do
  if [ -f "$json_file" ]; then
    query_name=$(basename "$json_file" .json)
    count=$(cat "$json_file" | jq '.results | length')
    echo "$query_name: $count 个漏洞"
  fi
done
echo ""

# 找出受影响最多的文件
echo "=== 高风险文件 Top 10 ==="
cat "$RESULTS_DIR"/*.json | jq -s 'flatten |
  .[].locations[].physicalLocation.artifactLocation.uri' |
  sort | uniq -c | sort -rn | head -10

echo ""

# 提取所有唯一的漏洞消息
echo "=== 漏洞类型统计 ==="
cat "$RESULTS_DIR"/*.json | jq -s 'flatten |
  .[].message.text' |
  sort | uniq -c | sort -rn

echo ""

# 生成合并报告
echo "=== 生成合并报告 ==="
cat "$RESULTS_DIR"/*.json | jq -s 'flatten | {
  total_vulnerabilities: length,
  unique_files: [.[].locations[].physicalLocation.artifactLocation.uri] | unique | length,
  by_type: group_by(.message.text) | map({type: .[0].message.text, count: length}),
  by_severity: group_by(.properties.severity // "unknown") | map({severity: .[0].properties.severity // "unknown", count: length})
}' > results/merged-report.json

echo "合并报告: results/merged-report.json"
cat results/merged-report.json | jq
```

**使用 jq 进行高级分析**:

```bash
# 统计所有查询的结果总数
jq -s '[.[] | .results | length] | add' results/test/*.json

# 找出所有查询都标记的文件
jq -s '[.[] | .results[].locations[].physicalLocation.artifactLocation.uri] |
  group_by(.) | map(select(length >= 2) | .[0])' results/test/*.json

# 按文件聚合漏洞
jq -s 'flatten |
  group_by(.locations[].physicalLocation.artifactLocation.uri) |
  map({
    file: .[0].locations[].physicalLocation.artifactLocation.uri,
    vulnerabilities: [.[] | {type: .message.text, line: .locations[].physicalLocation.region.startLine}]
  })' results/test/*.json

# 提取 Critical 级别的漏洞
jq -s 'flatten |
  map(select(.properties.severity == "critical"))' results/test/*.json
```

## Output Analysis

### JSON Result Structure（主要格式）

JSON 格式是最常用和可读性最好的格式，适合人工查看和脚本处理。

**完整 JSON 结构示例**:

```json
{
  "results": [
    {
      "ruleId": "path-traversal",
      "ruleIndex": 0,
      "message": {
        "text": "Path traversal from request.form.get('file')"
      },
      "locations": [
        {
          "physicalLocation": {
            "artifactLocation": {
              "uri": "app/controllers/upload.py",
              "index": 0
            },
            "region": {
              "startLine": 45,
              "startColumn": 15,
              "endLine": 45,
              "endColumn": 35
            }
          }
        }
      ],
      "properties": {
        "severity": "error",
        "security-severity": "9.8",
        "tags": ["security", "external/cwe/cwe-022"]
      }
    },
    {
      "ruleId": "path-traversal",
      "ruleIndex": 0,
      "message": {
        "text": "Path traversal from request.args.get('path')"
      },
      "locations": [
        {
          "physicalLocation": {
            "artifactLocation": {
              "uri": "app/controllers/filemanager.py",
              "index": 1
            },
            "region": {
              "startLine": 78,
              "startColumn": 10,
              "endLine": 78,
              "endColumn": 30
            }
          }
        }
      ],
      "properties": {
        "severity": "error",
        "security-severity": "9.8",
        "tags": ["security", "external/cwe/cwe-022"]
      }
    }
  ]
}
```

**字段说明**:

- `ruleId`: 规则标识符（漏洞类型）
- `message`: 漏洞描述
- `locations`: 漏洞位置数组
  - `artifactLocation.uri`: 受影响文件路径
  - `region.startLine`: 起始行号
  - `region.startColumn`: 起始列号
- `properties.severity`: 严重性级别
- `properties.security-severity`: 安全严重性评分（0-10）

**使用 jq 分析 JSON 结果**:

```bash
# 查看所有结果
cat results/test/cwe-022-path-traversal.json | jq '.results'

# 统计漏洞数量
cat results/test/cwe-022-path-traversal.json | jq '.results | length'

# 提取文件路径
cat results/test/cwe-022-path-traversal.json | jq -r '.results[].locations[].physicalLocation.artifactLocation.uri'

# 提取行号
cat results/test/cwe-022-path-traversal.json | jq '.results[].locations[].physicalLocation.region.startLine'

# 按严重性分组统计
cat results/test/cwe-022-path-traversal.json | jq '{
  critical: [.results[] | select(.properties.severity == "critical")] | length,
  high: [.results[] | select(.properties.severity == "error")] | length,
  medium: [.results[] | select(.properties.severity == "warning")] | length,
  low: [.results[] | select(.properties.severity == "note")] | length
}'

# 按文件分组统计
cat results/test/cwe-022-path-traversal.json | jq '[
  .results[]
  | {file: .locations[].physicalLocation.artifactLocation.uri, count: 1}
] | group_by(.file) | map({file: .[0].file, count: map(.count) | add}) | sort_by(.count) | reverse'

# 提取特定文件的所有漏洞
cat results/test/cwe-022-path-traversal.json | jq '.results[] | select(.locations[].physicalLocation.artifactLocation.uri == "app/controllers/upload.py")'

# 生成漏洞报告摘要
cat results/test/cwe-022-path-traversal.json | jq '{
  query: "path-traversal",
  total: (.results | length),
  unique_files: ([.results[].locations[].physicalLocation.artifactLocation.uri] | unique | length),
  severity_distribution: (
    .results | group_by(.properties.severity) |
    map({severity: .[0].properties.severity, count: length})
  ),
  top_files: (
    [.results[].locations[].physicalLocation.artifactLocation.uri] |
    group_by(.) |
    map({file: .[0], count: length}) |
    sort_by(.count) |
    reverse | .[0:5]
  )
}'

# 多个查询结果聚合
jq -s 'flatten | {
  total: length,
  by_type: (group_by(.ruleId) | map({type: .[0].ruleId, count: length})),
  by_severity: (group_by(.properties.severity) | map({severity: .[0].properties.severity, count: length}))
}' results/test/*.json
```

### SARIF Result Structure（补充格式）

SARIF (Static Analysis Results Interchange Format) 是标准化的结果格式，适合与 CI/CD 工具集成。

**SARIF 结构示例**:

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "CodeQL",
          "version": "2.12.5",
          "informationUri": "https://codeql.github.com/docs/",
          "rules": [
            {
              "id": "py/path-injection",
              "name": "Path injection",
              "shortDescription": {
                "text": "Path injection"
              },
              "fullDescription": {
                "text": "This query finds path injection vulnerabilities where user input is used in a file system operation."
              },
              "helpUri": "https://codeql.github.com/codeql-query-help/python/py-path-injection"
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "py/path-injection",
          "ruleIndex": 0,
          "level": "error",
          "message": {
            "text": "Path traversal from request.form.get('file')"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "app/controllers/upload.py",
                  "index": 0
                },
                "region": {
                  "startLine": 45,
                  "startColumn": 15,
                  "endLine": 45,
                  "endColumn": 35
                }
              }
            }
          ],
          "properties": {
            "security-severity": "9.8",
            "tags": ["security", "external/cwe/cwe-022"]
          }
        }
      ],
      "columnKind": "utf16CodeUnits"
    }
  ]
}
```

**SARIF 特点**:

- 标准化格式，兼容多种工具
- 包含工具和规则详细信息
- 适合 CI/CD 平台集成
- 支持丰富的元数据

**使用 jq 分析 SARIF 结果**:

```bash
# 统计结果数量
cat results/security.sarif | jq '.runs[].results | length'

# 按严重性分组
cat results/security.sarif | jq '[
  .runs[].results[] | {rule: .ruleId, severity: .level}
] | group_by(.rule) | map({rule: .[0].rule, count: length, severity: .[0].severity})'

# 提取所有规则
cat results/security.sarif | jq '.runs[].tool.driver.rules[].id'

# 按规则分组统计
cat results/security.sarif | jq '[
  .runs[].results[] | {rule: .ruleId, count: 1}
] | group_by(.rule) | map({rule: .[0].rule, count: map(.count) | add}) | sort_by(.count) | reverse'
```

### Results Interpretation Guide

**严重性级别**:
| 级别 | 安全评分 | 说明 |
|------|----------|------|
| critical | 9.0-10.0 | 极严重，立即修复 |
| error | 7.0-8.9 | 高危，尽快修复 |
| warning | 4.0-6.9 | 中危，计划修复 |
| note | 0.1-3.9 | 低危，可选修复 |

**常见漏洞类型**:
| 漏洞类型 | CWE | 严重性 |
|----------|-----|--------|
| Command Injection | CWE-78 | Critical |
| SQL Injection | CWE-89 | Critical |
| Path Traversal | CWE-22 | High |
| XSS | CWE-79 | High |
| Deserialization | CWE-502 | Critical |
| SSRF | CWE-918 | High |

**结果处理流程**:

1. **快速扫描**: 使用查询套件进行全面扫描
2. **结果汇总**: 使用 jq 聚合多个查询结果
3. **优先级排序**: 按严重性和影响范围排序
4. **人工审查**: 重点审查 Critical 和 High 级别漏洞
5. **修复验证**: 修复后重新运行查询验证

## Troubleshooting

### Common Issues

#### 1. Python Command Not Found

**问题**: `python3: command not found`

**解决方案**:

```bash
# 检查 Python 安装
which python3
which python

# 如果只有 python 可用，修改命令为:
python codeql-query.py ...

# 或创建别名
alias python3=python

# 永久添加到 ~/.bashrc 或 ~/.zshrc
echo 'alias python3=python' >> ~/.bashrc
source ~/.bashrc
```

#### 2. Database Not Found

**问题**: `Database not found or invalid`

**解决方案**:

```bash
# 检查数据库是否存在
ls -la database/WebGoat

# 检查数据库结构
ls -la database/WebGoat/*.db

# 使用 CodeQL CLI 检查数据库
/path/to/codeql database info database/WebGoat

# 确保数据库路径正确
# 相对路径应该从项目根目录开始
```

#### 3. Query File Not Found

**问题**: `Query file not found: codeql-queries/test/cwe-022-path-traversal.ql`

**解决方案**:

```bash
# 检查查询文件是否存在
ls -la codeql-queries/test/

# 列出所有查询文件
find codeql-queries -name "*.ql" -type f

# 检查文件路径拼写
# 确保使用正确的路径分隔符（Linux/Mac 使用 /，Windows 使用 \）
```

#### 4. Query Execution Failed

**问题**: `Query execution failed: ...`

**解决方案**:

```bash
# 检查查询语法（使用 CodeQL CLI）
/path/to/codeql query check codeql-queries/test/cwe-022-path-traversal.ql

# 查看详细错误信息
python3 codeql-query.py --verbose analyze \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output results.json

# 检查数据库完整性
/path/to/codeql database info database/WebGoat

# 确保查询语言与数据库语言匹配
# Python 查询只能在 Python 数据库上运行
```



#### 7. Permission Denied

**问题**: `Permission denied: cannot write to output directory`

**解决方案**:

```bash
# 检查输出目录权限
ls -la results/

# 创建输出目录并设置权限
mkdir -p results/test
chmod 755 results/test
```

### Debug Tips

**启用详细输出**:

```bash
# 查看详细执行信息
python3 codeql-query.py --verbose analyze \
  --database database/WebGoat \
  --query codeql-queries/test/cwe-022-path-traversal.ql \
  --output results.bqrs

# 或使用 CodeQL CLI 的调试选项
/path/to/codeql query run \
  --database=database/WebGoat \
  --verbose \
  query.ql
```

**检查环境变量**:

```bash
# 检查 Python 路径
which python3
echo $PATH

# 检查 CodeQL 路径
which codeql
echo $CODEQL_HOME

# 设置 CodeQL 路径（如果需要）
export CODEQL_HOME=/path/to/codeql
export PATH=$PATH:$CODEQL_HOME
```

**验证脚本权限**:

```bash
# 检查脚本是否可执行
ls -l codeql-query.py

# 如果需要，添加执行权限
chmod +x codeql-query.py
```

## Best Practices

### Query Execution

1. ** organize Queries by Category**

   ```bash
   codeql-queries/
   ├── critical/     # 高危漏洞查询
   ├── high/         # 高风险漏洞查询
   ├── medium/       # 中等风险漏洞查询
   └── custom/       # 自定义查询
   ```

2. **Use Consistent Naming**

   ```bash
   # 好的命名
   cwe-022-path-traversal.ql
   cwe-078-command-injection.ql
   business-logic-vulns.ql

   # 避免模糊命名
   test1.ql
   query2.ql
   vuln-check.ql
   ```

3. **Track Query Results**

   ```bash
   # 为每次扫描创建时间戳目录
   results/scan-20240128-143052/
   ├── cwe-022-path-traversal.json
   ├── cwe-078-command-injection.json
   └── summary.txt
   ```

4. **Batch Processing**
   ```bash
   # 使用脚本批量执行查询
   for query in codeql-queries/critical/*.ql; do
     python3 codeql-query.py analyze \
       --database database/WebGoat \
       --query "$query" \
       --output "results/$(basename $query .ql).bqrs"
   done
   ```

### Result Analysis

1. **Use jq for JSON Processing**

   ```bash
   # jq 是处理 JSON 的强大工具
   # 安装: brew install jq (Mac) 或 apt-get install jq (Linux)
   ```

2. **Maintain Result History**

   ```bash
   # 保留历史结果用于趋势分析
   results/
   ├── scan-20240128/
   ├── scan-20240129/
   └── scan-20240130/
   ```

3. **Prioritize Findings**

   ```bash
   # 按严重性排序
   jq '.results | sort_by(.properties.security-severity) | reverse' results.json

   # 先处理 Critical 和 High 级别
   jq '[.results[] | select(.properties.severity == "critical" or .properties.severity == "error")]' results.json
   ```

4. **Cross-Reference Results**
   ```bash
   # 对比多次扫描结果
   diff <(jq '.results[].locations[].physicalLocation.artifactLocation.uri' scan1.json | sort) \
        <(jq '.results[].locations[].physicalLocation.artifactLocation.uri' scan2.json | sort)
   ```

### Performance

1. **Reuse Database**

   ```bash
   # 不要为每个查询重新创建数据库
   # 对所有查询使用同一个数据库
   DATABASE="database/WebGoat"

   for query in codeql-queries/*.ql; do
     python3 codeql-query.py analyze \
       --database "$DATABASE" \
       --query "$query" \
       --output "results/$(basename $query .ql).bqrs"
   done
   ```

2. **Parallel Query Execution**

   ```bash
   # 并行运行独立查询
   find codeql-queries/test -name "*.ql" | parallel -j 4 \
     'python3 codeql-query.py analyze \
       --database database/WebGoat \
       --query {} \
       --output results/{/.}.bqrs'
   ```

3. **Result Caching**

   ```bash
   # 缓存解码后的 JSON 结果
   # 避免重复解码
   if [ ! -f results/decoded.json ]; then
     python3 codeql-query.py decode-bqrs \
       --input results/raw.bqrs \
       --format json \
       --output results/decoded.json
   fi
   ```

4. **Selective Query Execution**
   ```bash
   # 只运行相关的查询
   # 例如，只运行与文件操作相关的查询
   for query in codeql-queries/test/cwe-022-*.ql; do
     python3 codeql-query.py analyze \
       --database database/WebGoat \
       --query "$query" \
       --output "results/$(basename $query .ql).bqrs"
   done
   ```

## Additional Resources

### Official Documentation

- **CodeQL Documentation**: https://codeql.github.com/docs/
- **Query Help**: https://codeql.github.com/codeql-query-help/
- **SARIF Documentation**: https://sarifweb.azurewebsites.net/
- **GitHub Security Lab**: https://securitylab.github.com/

### Tools

- **jq**: Command-line JSON processor

  - Website: https://stedolan.github.io/jq/
  - Install (Mac): `brew install jq`
  - Install (Linux): `sudo apt-get install jq`

- **CodeQL CLI**:
  - GitHub: https://github.com/github/codeql-cli-binaries/releases
  - Documentation: https://codeql.github.com/docs/codeql-cli/

### Learning Resources

- **CodeQL Tutorials**: https://codeql.github.com/docs/codeql-overview/about-codeql-learning-resources/
- **Security Query Examples**: https://github.com/github/codeql/tree/main/ql
- **CWE List**: https://cwe.mitre.org/data/

---

**需要帮助处理特定场景？询问关于：**

- 在特定数据库上运行查询
- 分析查询套件的结果
- 对比多个查询结果
- 将结果集成到安全报告中
- 解决特定的错误或问题
