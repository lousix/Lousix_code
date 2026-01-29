# OpenCode 漏洞发现工作流 - 实现指南

## 概述

本文档详细说明了如何实现和使用OpenCode漏洞发现工作流，包括每个Agent的具体实现细节。

## 系统架构

```
WorkflowOrchestrator (Python主程序)
    │
    ├─── Initialization Agent (项目初始化)
    ├─── Sink Analyzer Agent (Sink点分析)
    ├─── Source Tracker Agent (Source追踪 - CodeQL+LSP)
    ├─── Context Analyzer Agent (上下文分析)
    └─── Reporter Agent (报告生成)
```

## Agent实现指南

### 1. Initialization Agent

**职责**: 识别和收集项目信息

**实现要点**:

```python
class InitializationAgent:
    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def scan_project(self):
        """扫描项目目录"""
        source_files = []
        for ext in [".py", ".js", ".ts", ".java", ".c", ".cpp"]:
            files = list(self.project_path.rglob(f"*{ext}"))
            source_files.extend(files)

        # 过滤排除的目录
        excluded = ["node_modules", ".git", "test", "vendor"]
        filtered = [
            str(f.relative_to(self.project_path))
            for f in source_files
            if not any(excl in str(f) for excl in excluded)
        ]

        return {
            "project_name": self.project_path.name,
            "total_files": len(filtered),
            "source_files": filtered,
        }

    def detect_language(self, file_path):
        """检测文件语言"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
        }
        return lang_map.get(ext, "Unknown")
```

**输出示例**:

```json
{
  "project_name": "my-project",
  "root_path": "/path/to/project",
  "total_files": 150,
  "languages": [
    {"language": "Python", "file_count": 100, "extension": ".py"},
    {"language": "TypeScript", "file_count": 50, "extension": ".ts"}
  ],
  "source_files": [
    {
      "path": "app/views.py",
      "language": "Python",
      "size": 2048
    }
  ]
}
```

### 2. Sink Analyzer Agent

**职责**: 识别代码中的潜在sink点

**实现要点**:

```python
class SinkAnalyzerAgent:
    def __init__(self):
        # 定义各语言的危险函数
        self.sink_patterns = {
            "Python": {
                "command_injection": [
                    r"\bos\.system\s*\(",
                    r"\bsubprocess\.\w+\s*\(",
                    r"\beval\s*\(",
                    r"\bexec\s*\(",
                ],
                "sql_injection": [
                    r"cursor\.execute\s*\(",
                    r"engine\.execute\s*\(",
                ],
                "path_traversal": [
                    r"\bopen\s*\(",
                    r"\bos\.path\.join\s*\(",
                ],
            },
            "JavaScript": {
                "xss": [
                    r"\.innerHTML\s*=",
                    r"\.outerHTML\s*=",
                ],
                "command_injection": [
                    r"child_process\.\w+\s*\(",
                    r"\beval\s*\(",
                ],
            },
        }

    def analyze_file(self, file_path, language):
        """分析单个文件"""
        sinks = []

        with open(file_path, "r") as f:
            content = f.read()
            lines = content.split("\n")

        patterns = self.sink_patterns.get(language, {})

        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count("\n") + 1
                    sinks.append({
                        "file": file_path,
                        "line": line_num,
                        "type": vuln_type,
                        "code": lines[line_num - 1].strip(),
                    })

        return sinks

    def analyze_all_files(self, project_info):
        """分析所有文件"""
        all_sinks = []

        for file_info in project_info["source_files"]:
            file_path = Path(project_info["root_path"]) / file_info["path"]
            language = file_info["language"]
            sinks = self.analyze_file(file_path, language)
            all_sinks.extend(sinks)

        return {
            "total_sinks": len(all_sinks),
            "sinks": all_sinks,
        }
```

### 3. Source Tracker Agent

**职责**: 使用CodeQL和LSP追踪数据流

**实现要点**:

#### 使用CodeQL

```python
class SourceTrackerAgent:
    def __init__(self):
        self.codeql_path = "codeql"  # 或使用完整路径

    def create_codeql_database(self, project_path, language):
        """创建CodeQL数据库"""
        cmd = [
            self.codeql_path,
            "database",
            "create",
            "my-db",
            f"--language={language}",
            f"--source-root={project_path}",
        ]
        subprocess.run(cmd, check=True)

    def run_codeql_query(self, query_file, database_path):
        """运行CodeQL查询"""
        cmd = [
            self.codeql_path,
            "query",
            "run",
            "--database", database_path,
            query_file,
            "--output=results.bqrs",
        ]
        subprocess.run(cmd, check=True)

        # 解析结果
        cmd = [
            self.codeql_path,
            "bqrs",
            "decode",
            "--format=json",
            "results.bqrs",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
```

#### 自定义CodeQL查询示例

```ql
// Python命令注入查询
import python

from DataFlow::Node source, DataFlow::Node sink
where exists(DataFlow::Configuration cfg |
  cfg.hasFlow(source, sink) and
  source instanceof ExternalRead and
  sink instanceof SystemExecution
)
select sink, "Command injection from $@", source, source
```

#### 使用LSP

```python
class LSPClient:
    def __init__(self, language):
        self.language = language
        self.server_process = None
        self.start_lsp_server()

    def start_lsp_server(self):
        """启动LSP服务器"""
        server_cmd = {
            "Python": "pylsp",
            "JavaScript": "typescript-language-server",
            "TypeScript": "typescript-language-server",
        }.get(self.language)

        if server_cmd:
            self.server_process = subprocess.Popen(
                [server_cmd, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def get_definition(self, file_path, line, column):
        """获取符号定义"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {"uri": f"file://{file_path}"},
                "position": {"line": line, "character": column},
            },
        }

        # 发送请求到LSP服务器
        self.server_process.stdin.write(json.dumps(request) + "\n")
        self.server_process.stdin.flush()

        # 读取响应
        response = self.server_process.stdout.readline()
        return json.loads(response)

    def find_references(self, file_path, line, column):
        """查找所有引用"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "textDocument/references",
            "params": {
                "textDocument": {"uri": f"file://{file_path}"},
                "position": {"line": line, "character": column},
            },
        }

        self.server_process.stdin.write(json.dumps(request) + "\n")
        self.server_process.stdin.flush()

        response = self.server_process.stdout.readline()
        return json.loads(response)
```

### 4. Context Analyzer Agent

**职责**: 分析上下文，验证漏洞

**实现要点**:

```python
class ContextAnalyzerAgent:
    def __init__(self):
        self.validation_patterns = {
            "length_check": [
                r"len\s*\(\s*\w+\s*\)\s*[<>]=?\s*\d+",
                r"\.length\s*[<>]=?\s*\d+",
            ],
            "whitelist": [
                r"\w+\s+in\s+\w+",
            ],
        }

        self.sanitization_patterns = {
            "html_escape": [
                r"escape\s*\(",
                r"escapeHtml\s*\(",
            ],
            "sql_escape": [
                r"execute\s*\([^)]*%\s*\w+",
            ],
        }

    def extract_function_context(self, file_path, line_num, context_lines=10):
        """提取函数上下文"""
        with open(file_path, "r") as f:
            lines = f.readlines()

        start = max(0, line_num - context_lines)
        end = min(len(lines), line_num + context_lines)

        return "".join(lines[start:end])

    def check_validation(self, context):
        """检查是否存在校验"""
        for vuln_type, patterns in self.validation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context):
                    return True, vuln_type
        return False, None

    def check_sanitization(self, context):
        """检查是否存在净化"""
        for vuln_type, patterns in self.sanitization_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context):
                    return True, vuln_type
        return False, None

    def calculate_confidence(self, has_validation, has_sanitization):
        """计算置信度"""
        confidence = 1.0

        if has_validation:
            confidence -= 0.2

        if has_sanitization:
            confidence -= 0.3

        return max(0.0, confidence)

    def analyze_path(self, dataflow_path):
        """分析单个数据流路径"""
        results = []

        for node in dataflow_path["nodes"]:
            file_path = node["file"]
            line_num = node["line"]

            # 提取上下文
            context = self.extract_function_context(file_path, line_num)

            # 检查校验
            has_valid, valid_type = self.check_validation(context)

            # 检查净化
            has_sani, sani_type = self.check_sanitization(context)

            # 计算置信度
            confidence = self.calculate_confidence(has_valid, has_sani)

            results.append({
                "file": file_path,
                "line": line_num,
                "has_validation": has_valid,
                "has_sanitization": has_sani,
                "confidence": confidence,
            })

        return results
```

### 5. Reporter Agent

**职责**: 生成报告

**实现要点**:

```python
class ReporterAgent:
    def __init__(self):
        self.template = self.load_template()

    def generate_markdown_report(self, verified_vulns, project_info):
        """生成Markdown报告"""

        report = f"""# 漏洞扫描报告

## 执行摘要

| 项目 | 信息 |
|------|------|
| 项目名称 | {project_info['project_name']} |
| 扫描时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| 扫描工具 | OpenCode Vulnerability Scanner |
| 分析方法 | CodeQL + LSP + 静态分析 |
| 扫描文件数 | {project_info['total_files']} |

### 风险概览

| 严重性 | 数量 | 占比 |
|--------|------|------|
| 🔴 Critical | {verified_vulns['by_severity']['Critical']} | - |
| 🟠 High | {verified_vulns['by_severity']['High']} | - |
| 🟡 Medium | {verified_vulns['by_severity']['Medium']} | - |
| 🟢 Low | {verified_vulns['by_severity']['Low']} | - |
| **总计** | **{verified_vulns['verified_vulnerabilities']}** | - |

"""

        # 添加漏洞详情
        report += self._generate_vulnerability_details(verified_vulns)

        return report

    def generate_json_report(self, verified_vulns, project_info):
        """生成JSON报告"""

        return {
            "metadata": {
                "project_name": project_info["project_name"],
                "scan_time": datetime.now().isoformat(),
                "scanner": "OpenCode Vulnerability Scanner",
            },
            "summary": {
                "total_files": project_info["total_files"],
                "total_vulnerabilities": verified_vulns["verified_vulnerabilities"],
                "by_severity": verified_vulns["by_severity"],
            },
            "vulnerabilities": verified_vulns["vulnerabilities"],
        }

    def save_report(self, content, format="markdown"):
        """保存报告"""
        if format == "markdown":
            path = "reports/vulnerability_report.md"
        elif format == "json":
            path = "reports/vulnerability_report.json"

        with open(path, "w", encoding="utf-8") as f:
            if format == "json":
                json.dump(content, f, indent=2)
            else:
                f.write(content)

        return path
```

## 完整工作流示例

```python
def main():
    # 1. 初始化
    init_agent = InitializationAgent(project_path)
    project_info = init_agent.scan_project()

    # 2. Sink分析
    sink_agent = SinkAnalyzerAgent()
    sink_points = sink_agent.analyze_all_files(project_info)

    # 3. Source追踪
    source_agent = SourceTrackerAgent()
    source_agent.create_codeql_database(project_path, "Python")
    dataflow_paths = source_agent.trace_sources(sink_points)

    # 4. 上下文分析
    context_agent = ContextAnalyzerAgent()
    verified_vulns = context_agent.analyze_all_paths(dataflow_paths)

    # 5. 报告生成
    reporter = ReporterAgent()
    reporter.generate_markdown_report(verified_vulns, project_info)
    reporter.generate_json_report(verified_vulns, project_info)

    print("扫描完成！")
```

## 性能优化建议

1. **并行处理**: 使用多进程/多线程并行分析文件
2. **缓存**: 缓存LSP查询结果
3. **增量扫描**: 只分析变更的文件
4. **优先级排序**: 优先分析高风险文件

## 扩展和定制

### 添加新的漏洞类型

1. 在`sink_patterns`中添加新模式
2. 在`validation_patterns`中添加新的校验模式
3. 在`sanitization_patterns`中添加新的净化模式

### 支持新的语言

1. 添加新的LSP服务器配置
2. 定义语言的危险函数列表
3. 编写对应的CodeQL查询

### 自定义报告格式

1. 修改`ReporterAgent`的模板
2. 添加新的输出格式（HTML、PDF等）
3. 自定义报告样式和结构
