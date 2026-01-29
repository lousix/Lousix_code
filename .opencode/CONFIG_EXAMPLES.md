# OpenCode 漏洞发现工作流 - 配置示例

## 基础配置 (workflow-config.yaml)

```yaml
# 工作流基础配置
workflow:
  name: vulnerability-discovery
  version: 1.0.0
  description: 自动化漏洞发现工作流

# 工作目录
working_dir: ./Lousix_code

# 输出目录配置
output:
  base_dir: .opencode/reports
  formats:
    - markdown  # Markdown格式报告
    - json      # JSON格式报告
    - html      # HTML格式报告（可选）

# Agent配置
agents:
  initialization:
    enabled: true
    timeout: 60
    exclude_dirs:
      - node_modules
      - .git
      - test
      - tests
      - vendor
      - dist
      - build
      - __pycache__
    include_extensions:
      - .py
      - .js
      - .ts
      - .java
      - .c
      - .cpp
      - .go
      - .rb
      - .php

  sink_analyzer:
    enabled: true
    timeout: 300
    max_files_per_batch: 50
    parallel_workers: 4

  source_tracker:
    enabled: true
    timeout: 600
    use_codeql: true
    use_lsp: true
    codeql_path: codeql  # 或完整路径 /usr/local/bin/codeql
    max_depth: 5
    max_paths_per_sink: 10

  context_analyzer:
    enabled: true
    timeout: 300
    context_lines: 10
    confidence_threshold: 0.5

  reporter:
    enabled: true
    timeout: 60
    include_code_snippets: true
    max_snippet_lines: 20
    sort_by: severity  # severity, confidence, file
```

## CodeQL配置

### Python项目配置

```yaml
codeql:
  enabled: true
  language: python

  # 数据库配置
  database:
    name: python-db
    location: .opencode/codeql-databases
    build_command:  # 可选，如果项目需要构建
      - python
      - -m
      - pip
      - install
      - -e
      - .

  # 查询配置
  queries:
    - name: security-queries
      path: codeql/python-queries:Security
      include:
        - CWE-078  # 命令注入
        - CWE-089  # SQL注入
        - CWE-022  # 路径遍历
        - CWE-502  # 反序列化

    - name: custom-queries
      path: .opencode/queries/custom
```

### JavaScript/TypeScript配置

```yaml
codeql:
  enabled: true
  language: javascript

  database:
    name: js-db
    location: .opencode/codeql-databases

  queries:
    - name: security-queries
      path: codeql/javascript-queries:Security
      include:
        - CWE-078  # 命令注入
        - CWE-079  # XSS
        - CWE-022  # 路径遍历
```

### Java项目配置

```yaml
codeql:
  enabled: true
  language: java

  database:
    name: java-db
    location: .opencode/codeql-databases
    build_command:
      - mvn
      - clean
      - install
      - -DskipTests

  queries:
    - name: security-queries
      path: codeql/java-queries:Security
      include:
        - CWE-089  # SQL注入
        - CWE-078  # 命令注入
        - CWE-022  # 路径遍历
        - CWE-502  # 反序列化
```

## LSP配置

```yaml
lsp:
  enabled: true
  timeout: 30
  retry_count: 3

  # 语言服务器配置
  servers:
    python:
      command: pylsp
      args: []
      enabled: true

    javascript:
      command: typescript-language-server
      args: ["--stdio"]
      enabled: true

    typescript:
      command: typescript-language-server
      args: ["--stdio"]
      enabled: true

    java:
      command: java
      args:
        - -jar
        - /path/to/jdt-language-server.jar
      enabled: true

    go:
      command: gopls
      args: ["serve"]
      enabled: true

    c:
      command: clangd
      args: []
      enabled: true

    cpp:
      command: clangd
      args: []
      enabled: true

  # 缓存配置
  cache:
    enabled: true
    location: .opencode/lsp-cache
    max_age: 3600  # 缓存有效期（秒）
```

## 漏洞规则配置

```yaml
vulnerability_rules:

  # Python漏洞规则
  python:
    command_injection:
      enabled: true
      severity: Critical
      cwe: CWE-78
      patterns:
        - r"\bos\.system\s*\("
        - r"\bsubprocess\.\w+\s*\("
        - r"\bexec\s*\("
        - r"\beval\s*\("
      sinks:
        - function: os.system
        - function: subprocess.run
        - function: subprocess.call
        - function: subprocess.Popen
        - function: eval
        - function: exec

    sql_injection:
      enabled: true
      severity: High
      cwe: CWE-89
      patterns:
        - r"cursor\.execute\s*\("
        - r"engine\.execute\s*\("
      sinks:
        - function: cursor.execute
        - function: engine.execute

    path_traversal:
      enabled: true
      severity: High
      cwe: CWE-022
      patterns:
        - r"\bopen\s*\("
        - r"\bos\.path\.join\s*\("
      sinks:
        - function: open
        - function: os.path.join

    xss:
      enabled: true
      severity: Medium
      cwe: CWE-079
      patterns:
        - r"HttpResponse\s*\("
        - r"render_template\s*\("
      sinks:
        - function: django.HttpResponse
        - function: flask.render_template

  # JavaScript漏洞规则
  javascript:
    xss:
      enabled: true
      severity: High
      cwe: CWE-079
      patterns:
        - r"\.innerHTML\s*="
        - r"\.outerHTML\s*="
      sinks:
        - property: innerHTML
        - property: outerHTML

    command_injection:
      enabled: true
      severity: Critical
      cwe: CWE-078
      patterns:
        - r"child_process\.\w+\s*\("
        - r"\beval\s*\("
      sinks:
        - function: eval
        - function: child_process.exec
        - function: child_process.spawn

  # Java漏洞规则
  java:
    sql_injection:
      enabled: true
      severity: High
      cwe: CWE-089
      patterns:
        - r"Statement\.execute"
        - r"PreparedStatement"
      sinks:
        - method: Statement.execute
        - method: PreparedStatement.execute

    command_injection:
      enabled: true
      severity: Critical
      cwe: CWE-078
      patterns:
        - r"Runtime\.exec"
        - r"ProcessBuilder"
      sinks:
        - method: Runtime.exec
        - class: ProcessBuilder
```

## 校验规则配置

```yaml
validation_rules:
  python:
    length_check:
      pattern: r"len\s*\(\s*\w+\s*\)\s*[<>]=?\s*\d+"
      severity_reduction: 0.1

    whitelist_check:
      pattern: r"\w+\s+in\s+ALLOWED"
      severity_reduction: 0.2

    type_check:
      pattern: r"isinstance\s*\(\s*\w+"
      severity_reduction: 0.1

    regex_validation:
      pattern: r"re\.(match|search|fullmatch)\s*\("
      severity_reduction: 0.2

  javascript:
    length_check:
      pattern: r"\.length\s*[<>]=?\s*\d+"
      severity_reduction: 0.1

    whitelist_check:
      pattern: r"\.includes\s*\("
      severity_reduction: 0.2

    type_check:
      pattern: r"typeof\s+\w+\s*==="
      severity_reduction: 0.1
```

## 净化规则配置

```yaml
sanitization_rules:
  python:
    html_escape:
      patterns:
        - r"escape\s*\("
        - r"html\.escape\s*\("
      applies_to: [xss]
      severity_reduction: 0.3

    sql_escape:
      patterns:
        - r"execute\s*\([^)]*%\s*\w+"
        - r"execute\s*\([^)]*\?\s*\w+"
      applies_to: [sql_injection]
      severity_reduction: 0.3

    path_normalization:
      patterns:
        - r"os\.path\.normpath\s*\("
        - r"os\.path\.abspath\s*\("
      applies_to: [path_traversal]
      severity_reduction: 0.2

  javascript:
    html_escape:
      patterns:
        - r"escapeHtml\s*\("
        - r"sanitize\s*\("
      applies_to: [xss]
      severity_reduction: 0.3

    path_normalization:
      patterns:
        - r"path\.normalize\s*\("
      applies_to: [path_traversal]
      severity_reduction: 0.2
```

## 报告配置

```yaml
report:
  # 报告格式
  format:
    markdown:
      enabled: true
      filename: vulnerability_report.md
      include_code_snippets: true
      max_snippet_lines: 15
      use_emoji: true

    json:
      enabled: true
      filename: vulnerability_report.json
      pretty_print: true

    html:
      enabled: false
      filename: vulnerability_report.html
      theme: light

  # 排序配置
  sort:
    by: severity  # severity, confidence, file, line
    order: desc   # asc, desc

  # 过滤配置
  filter:
    min_severity: Low  # Low, Medium, High, Critical
    min_confidence: 0.3

  # 统计配置
  statistics:
    by_severity: true
    by_type: true
    by_file: true
    by_confidence: true

  # 修复建议
  recommendations:
    enabled: true
    include_code_examples: true
    language: auto  # auto, python, javascript, etc.
```

## 性能配置

```yaml
performance:
  # 并发配置
  concurrency:
    max_workers: 4
    batch_size: 20

  # 缓存配置
  cache:
    enabled: true
    location: .opencode/cache
    max_size: 1000
    ttl: 3600

  # 超时配置
  timeout:
    initialization: 60
    sink_analysis: 300
    source_tracking: 600
    context_analysis: 300
    report_generation: 60

  # 内存限制
  memory:
    max_usage: "2GB"
    gc_threshold: 1000
```

## 日志配置

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "[%(asctime)s] [%(levelname)s] %(message)s"
  output:
    - console
    - file: .opencode/logs/workflow.log

  # 特定模块的日志级别
  modules:
    codeql: WARNING
    lsp: INFO
    sink_analyzer: DEBUG
    source_tracker: INFO
```

## 示例：完整配置文件

```yaml
# OpenCode 漏洞发现工作流 - 完整配置

workflow:
  name: vulnerability-discovery
  version: 1.0.0
  working_dir: ./Lousix_code

codeql:
  enabled: true
  language: python
  database:
    location: .opencode/codeql-databases
  queries:
    - path: codeql/python-queries:Security

lsp:
  enabled: true
  servers:
    python:
      command: pylsp
      enabled: true

vulnerability_rules:
  python:
    command_injection:
      enabled: true
      severity: Critical
    sql_injection:
      enabled: true
      severity: High

report:
  format:
    markdown:
      enabled: true
    json:
      enabled: true

performance:
  concurrency:
    max_workers: 4

logging:
  level: INFO
  output:
    - console
    - file: .opencode/logs/workflow.log
```

## 使用自定义配置

```bash
# 使用自定义配置文件运行
python workflow.py --config custom-config.yaml

# 或者设置环境变量
export OPENCODE_CONFIG=custom-config.yaml
python workflow.py
```
