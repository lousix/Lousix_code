# CodeQL 查询库

本目录包含用于安全漏洞检测的 CodeQL 查询文件。

## 目录结构

```
codeql-queries/
├── java/                    # Java 查询文件
│   ├── cwe-089-sql-injection.ql
│   ├── cwe-079-xss.ql
│   ├── cwe-022-path-traversal.ql
│   ├── cwe-502-deserialization.ql
│   ├── cwe-352-csrf.ql
│   ├── cwe-078-command-injection.ql
│   ├── cwe-601-url-redirect.ql
│   └── suites/              # 查询套件目录
│       └── security-default.qls
└── README.md
```

## 查询文件说明

### CWE-089: SQL 注入 (cwe-089-sql-injection.ql)
检测用户输入未经过滤直接流入 SQL 查询的情况。

### CWE-079: 跨站脚本攻击 (cwe-079-xss.ql)
检测用户输入未经过滤直接输出到 HTML 的情况。

### CWE-022: 路径遍历 (cwe-022-path-traversal.ql)
检测用户输入未经过滤直接用于文件路径的情况。

### CWE-502: 不安全的反序列化 (cwe-502-deserialization.ql)
检测用户输入直接用于反序列化操作的情况。

### CWE-352: 跨站请求伪造 (cwe-352-csrf.ql)
检测状态变更操作缺少 CSRF 保护的情况。

### CWE-078: 命令注入 (cwe-078-command-injection.ql)
检测用户输入未经过滤直接用于命令执行的情况。

### CWE-601: URL 重定向 (cwe-601-url-redirect.ql)
检测用户输入未经过滤直接用于 URL 重定向的情况。

## 查询套件

### security-default.qls
默认安全查询套件，包含以下查询：
- SQL 注入
- XSS
- 路径遍历
- 不安全的反序列化
- 命令注入

## 使用方法

### 使用查询套件（推荐）

```bash
codeql database analyze <database-path> \
  --format=sarif-latest \
  --output=results.sarif \
  codeql-queries/java/suites/security-default.qls
```

### 使用单个查询文件

```bash
codeql database analyze <database-path> \
  --format=sarif-latest \
  --output=results.sarif \
  codeql-queries/java/cwe-089-sql-injection.ql
```

### 使用多个查询文件

```bash
codeql database analyze <database-path> \
  --format=sarif-latest \
  --output=results.sarif \
  --max-paths=4 \
  codeql-queries/java/cwe-089-sql-injection.ql \
  codeql-queries/java/cwe-079-xss.ql \
  codeql-queries/java/cwe-022-path-traversal.ql
```

## 与 Agent 集成

这些查询文件与 `codeql-runner` agent 配合使用。支持的 `query_profile` 值：

- `security-default`: 使用 `codeql-queries/java/suites/security-default.qls`
- `cwe-high-risk`: 使用多个高危 CWE 查询脚本组合
- `cwe-sql-injection`: 使用 `cwe-089-sql-injection.ql`
- `cwe-xss`: 使用 `cwe-079-xss.ql`
- `cwe-path-traversal`: 使用 `cwe-022-path-traversal.ql`

## 注意事项

1. 这些查询文件需要与 CodeQL 标准库配合使用
2. 某些查询可能需要导入额外的 CodeQL 库（如 Spring 框架支持）
3. 查询结果可能包含误报，需要通过后续的 triage 流程进行验证
4. 建议定期更新查询文件以匹配最新的安全威胁模式

## 扩展查询

要添加新的查询文件：

1. 在 `codeql-queries/java/` 目录下创建新的 `.ql` 文件
2. 遵循 CodeQL 查询文件的标准格式
3. 在 `security-default.qls` 中添加引用（如果需要）
4. 更新 `codeql-runner.md` 中的 `query_profile` 映射表（如果需要）

## 参考资源

- [CodeQL 文档](https://codeql.github.com/docs/)
- [CodeQL 查询编写指南](https://codeql.github.com/docs/writing-codeql-queries/)
- [CWE 漏洞分类](https://cwe.mitre.org/)
