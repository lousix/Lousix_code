#!/usr/bin/env python3
"""
简单的 CodeQL 命令封装脚本。

支持功能：
- 运行单个查询（`database analyze` + .ql）
- 创建 CodeQL 数据库（`database create`）
- 运行查询套件 / 查询包（例如 `codeql/python-queries:Security`）

用法示例（在项目根目录执行）：

1. 运行单个查询（与之前兼容）：
   python codeql-query.py \
       --database database/WebGoat \
       --query codeql-queries/test/cwe-022-path-traversal.ql \
       --output database/WebGoat/results/test/cwe-022-path-traversal.json 

   或使用子命令形式：
   python codeql-query.py analyze \
       --database database/WebGoat \
       --query codeql-queries/test/cwe-022-path-traversal.ql \
       --output database/WebGoat/results/test/cwe-022-path-traversal.json 

2. 创建数据库（示例：为 WebGoat 创建 Java 数据库）：
   python codeql-query.py create-db \
       --database database/WebGoat \
       --source-root . \
       --language java \
       --command "./mvnw -q -DskipTests package"

3. 运行查询套件（如 python Security 套件，示例）：
   python codeql-query.py suite \
       --database database/PythonApp \
       --suite codeql/python-queries:Security \
       --format sarif \
       --output results/python-security.json

4. 指定 CodeQL 可执行文件路径（如果不在 PATH 中）：
   python codeql-query.py --codeql /path/to/codeql analyze ...
"""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def _run(cmd: Iterable[str]) -> int:
    cmd_list = list(map(str, cmd))
    print("执行命令：", " ".join(shlex.quote(c) for c in cmd_list))
    try:
        completed = subprocess.run(cmd_list, check=False)
    except FileNotFoundError as exc:
        print(f"找不到可执行文件：{cmd_list[0]}", file=sys.stderr)
        print(f"错误详情：{exc}", file=sys.stderr)
        return 1

    if completed.returncode != 0:
        print(f"命令执行失败，退出码：{completed.returncode}", file=sys.stderr)
    else:
        print("命令执行成功。")
    return completed.returncode


def run_analyze(database: Path, query: Path, output: Path, codeql: str) -> int:
    """
    调用 `codeql database analyze` 运行单个 .ql 查询，输出 json
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        codeql,
        "database",
        "analyze",
        str(database),
        str(query),
        "--format=sarif-latest",
        f"--output={output}",
        "--rerun"
    ]
    return _run(cmd)


def run_create_db(
    database: Path,
    source_root: Path,
    language: str,
    command: str | None,
    overwrite: bool,
    threads: int | None,
    codeql: str,
) -> int:
    """
    调用 `codeql database create` 创建数据库。
    """
    database.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        codeql,
        "database",
        "create",
        str(database),
        f"--language={language}",
        f"--source-root={source_root}",
    ]
    if command:
        cmd.extend(["--command", command])
    if overwrite:
        cmd.append("--overwrite")
    if threads is not None:
        cmd.append(f"--threads={threads}")

    return _run(cmd)


def run_suite(
    database: Path,
    suite: str,
    output: Path | None,
    fmt: str,
    threads: int | None,
    codeql: str,
) -> int:
    """
    调用 `codeql database analyze` 运行查询套件 / 查询包。
    例如：codeql/python-queries:Security 或 codeql/java-queries
    """
    cmd: list[str] = [
        codeql,
        "database",
        "analyze",
        str(database),
        suite,
        f"--format={fmt}",
    ]
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        cmd.append(f"--output={output}")
    if threads is not None:
        cmd.append(f"--threads={threads}")

    return _run(cmd)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="便捷运行 CodeQL 常用命令的脚本",
    )
    parser.add_argument(
        "--codeql",
        default="codeql",
        help="codeql 可执行文件名称或绝对路径（默认：codeql，需在 PATH 中）",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # analyze: 单个 .ql 查询（保持与旧版本功能一致）
    analyze = subparsers.add_parser(
        "analyze", help="对数据库运行单个 .ql 查询，输出 json"
    )
    analyze.add_argument(
        "--database",
        "-d",
        required=True,
        type=Path,
        help="CodeQL 数据库目录，例如 database/WebGoat",
    )
    analyze.add_argument(
        "--query",
        "-q",
        required=True,
        type=Path,
        help="CodeQL 查询文件路径，例如 codeql-queries/test/cwe-022-path-traversal.ql",
    )
    analyze.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="输出 .json 文件路径，例如 database/WebGoat/results/test/cwe-022-path-traversal.json",
    )

    # create-db: 创建数据库
    create_db = subparsers.add_parser(
        "create-db", help="创建 CodeQL 数据库（database create）"
    )
    create_db.add_argument(
        "--database",
        "-d",
        required=True,
        type=Path,
        help="要创建的数据库目录，例如 database/WebGoat",
    )
    create_db.add_argument(
        "--source-root",
        "-s",
        required=True,
        type=Path,
        help="源码根目录，例如当前项目根目录 .",
    )
    create_db.add_argument(
        "--language",
        "-l",
        default="java",
        help="编程语言（默认：java，例如 python、javascript 等）",
    )
    create_db.add_argument(
        "--command",
        help=(
            "构建命令，例如 \"./mvnw -q -DskipTests package\"；"
            "如果省略，则使用 CodeQL 的自动构建（若支持）"
        ),
    )
    create_db.add_argument(
        "--overwrite",
        action="store_true",
        help="如果数据库已存在则覆盖",
    )
    create_db.add_argument(
        "--threads",
        type=int,
        help="并发线程数，映射到 --threads",
    )

    # suite: 运行查询套件 / 查询包
    suite = subparsers.add_parser(
        "suite", help="对数据库运行查询套件 / 查询包（如 codeql/python-queries:Security）"
    )
    suite.add_argument(
        "--database",
        "-d",
        required=True,
        type=Path,
        help="CodeQL 数据库目录",
    )
    suite.add_argument(
        "--suite",
        "-s",
        required=True,
        help="查询套件或查询包标识，例如 codeql/python-queries:Security",
    )
    suite.add_argument(
        "--format",
        "-f",
        default="sarif",
        choices=["sarif-latest", "csv", "text", "json"],
        help="输出格式（默认：sarif）",
    )
    suite.add_argument(
        "--output",
        "-o",
        type=Path,
        help="输出文件路径（可选），例如 results/security.sarif",
    )
    suite.add_argument(
        "--threads",
        type=int,
        help="并发线程数，映射到 --threads",
    )

    # decode-bqrs: 解码 BQRS
    decode = subparsers.add_parser(
        "decode-bqrs", help="将 BQRS 结果文件解码为 JSON / SARIF 等格式"
    )
    decode.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="输入 BQRS 文件路径",
    )
    decode.add_argument(
        "--format",
        "-f",
        default="json",
        # choices=["json", "sarifv2", "csv", "text"],
        choices=["json", "sarif-latest", "csv", "CSV"],
        help="输出格式（默认：json；SARIF 使用 sarifv2）",
    )
    decode.add_argument(
        "--output",
        "-o",
        type=Path,
        help="输出文件路径（可选，默认输出到 stdout）",
    )

    # 为了兼容老用法：不写子命令时，按照 analyze 解析参数
    # 旧调用方式：python codeql-query.py --database ... --query ... --output ...
    parser.add_argument(
        "--database",
        "-D",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--query",
        "-Q",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--output",
        "-O",
        type=Path,
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args(argv)
    # 把 parser 附在 args 上，方便 main 中做兼容性处理时报错
    setattr(args, "_parser", parser)
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    parser: argparse.ArgumentParser = getattr(args, "_parser")

    # 兼容旧写法：没有子命令，但传了 --database/--query/--output
    if args.command is None and args.database and args.query and args.output:
        # 模拟 analyze 子命令的行为
        if not args.database.exists():
            print(f"数据库目录不存在：{args.database}", file=sys.stderr)
            return 1
        if not (args.query.is_file() or args.query.is_dir()):
            print(f"查询文件不存在：{args.query}", file=sys.stderr)
            return 1
        return run_analyze(
            database=args.database,
            query=args.query,
            output=args.output,
            codeql=args.codeql,
        )

    if args.command is None:
        parser.print_help(file=sys.stderr)
        return 1

    if args.command == "analyze":
        if not args.database.exists():
            print(f"数据库目录不存在：{args.database}", file=sys.stderr)
            return 1
        if not (args.query.is_file() or args.query.is_dir()):
            print(f"查询文件不存在：{args.query}", file=sys.stderr)
            return 1
        return run_analyze(
            database=args.database,
            query=args.query,
            output=args.output,
            codeql=args.codeql,
        )

    if args.command == "create-db":
        if not args.source_root.exists():
            print(f"源码根目录不存在：{args.source_root}", file=sys.stderr)
            return 1
        return run_create_db(
            database=args.database,
            source_root=args.source_root,
            language=args.language,
            command=args.command,
            overwrite=args.overwrite,
            threads=args.threads,
            codeql=args.codeql,
        )

    if args.command == "suite":
        if not args.database.exists():
            print(f"数据库目录不存在：{args.database}", file=sys.stderr)
            return 1
        return run_suite(
            database=args.database,
            suite=args.suite,
            output=args.output,
            fmt=args.format,
            threads=args.threads,
            codeql=args.codeql,
        )


    print(f"未知命令：{args.command}", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
