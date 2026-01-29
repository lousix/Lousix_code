# SQL注入漏洞数据流分析报告

## 概述

本报告分析了jshERP系统中的SQL注入漏洞数据流路径，重点分析了4个高风险的Sink点，追踪了从用户输入到SQL执行的完整数据流。

## 关键发现

### 1. Critical级别漏洞：QueryUtils.filter()方法中的动态SQL构建

**漏洞路径**: PATH-001 (SINK-002)

**数据流分析**:
1. **Source**: ResourceController.getList() 从HTTP请求中提取参数
2. **Transform**: CommonQueryManager.select() 和 UserComponent.select() 传递参数
3. **Sink**: QueryUtils.filter() 直接将用户输入拼接到SQL语句中

**关键代码**:
```java
// QueryUtils.java line 114-131
builder.append("`").append(key).append("`");
builder.append(" IN ");
builder.append("(");
for (int vidx = 0; vidx < value.size(); ++vidx) {
    builder.append(value.getString(vidx));
}
```

**攻击示例**:
```
filter=[{"name":"id","value":["1","1') OR '1'='1"]}]
```
生成SQL: `... WHERE (`id` IN (1,1') OR '1'='1))`

### 2. High级别漏洞：OrderUtils.getOrderString()中的ORDER BY子句构建

**漏洞路径**: PATH-002 (SINK-007) 和 PATH-003 (SINK-008)

**数据流分析**:
1. **Source**: ResourceController.getList() 从HTTP请求中提取参数
2. **Transform**: CommonQueryManager.select() 和 Component.select() 传递参数
3. **Sink**: OrderUtils.getOrderString() 直接将用户输入拼接到ORDER BY子句

**关键代码**:
```java
// OrderUtils.java line 24
return column + " " + splits[1];

// OrderUtils.java line 37
return "convert(" + tableName + "." + ColumnPropertyUtil.propertyToColumn(splits[0]) + " using gbk) " + splits[1];
```

**攻击示例**:
```
order=id; DROP TABLE jsh_user; --
```
生成SQL: `... ORDER BY id; DROP TABLE jsh_user; --`

### 3. High级别漏洞：UserComponent.getUserList()调用风险方法

**漏洞路径**: PATH-004 (SINK-014)

**数据流分析**:
1. **Source**: ResourceController.getList() 从HTTP请求中提取参数
2. **Transform**: CommonQueryManager.select() 和 UserComponent.getUserList() 传递参数
3. **Sink**: UserMapperEx.selectByConditionUser() 执行查询

**关键发现**:
- 虽然调用了QueryUtils.filter()，但实际查询使用的是MyBatis参数化查询
- MyBatis的bind标签提供了部分保护，但仍存在风险

## 数据流模式分析

### 1. 通用查询模式

系统使用了通用查询架构，通过以下组件链传递数据：
```
Controller -> CommonQueryManager -> InterfaceContainer -> Component -> Service -> Mapper
```

这种模式虽然提高了代码复用性，但也增加了攻击面，因为：
- 单一的入口点(ResourceController)可能被用于攻击多个资源
- 动态组件解析(通过apiName参数)增加了控制复杂性
- 参数传递链长，难以统一进行安全检查

### 2. 参数处理模式

系统中存在两种主要的参数处理模式：
1. **危险模式**: 直接字符串拼接构建SQL(QueryUtils.filter, OrderUtils.getOrderString)
2. **相对安全模式**: MyBatis参数化查询(使用bind标签和#{}占位符)

## 攻击向量总结

### 1. filter参数注入
- **位置**: IN子句值列表
- **影响**: 可能导致SQL注入，绕过认证，数据泄露
- **难度**: 低

### 2. order参数注入
- **位置**: ORDER BY子句
- **影响**: 可能导致SQL注入，数据泄露，执行任意SQL
- **难度**: 中

### 3. apiName参数注入
- **位置**: 动态组件解析
- **影响**: 可能访问未授权的资源
- **难度**: 高

## 修复建议

### 1. 立即修复建议

1. **filter参数处理**:
   - 使用参数化查询代替字符串拼接
   - 实现严格的输入验证和类型检查
   - 使用白名单验证字段名和值

2. **order参数处理**:
   - 实现字段名白名单验证
   - 限制排序方向(只允许ASC/DESC)
   - 避免直接拼接用户输入

### 2. 长期架构改进

1. **统一输入验证**:
   - 在Controller层实现统一的参数验证
   - 使用Spring Validation注解
   - 实现自定义验证器处理复杂场景

2. **查询安全框架**:
   - 使用ORM框架提供的安全查询方法
   - 实现查询构建器模式，避免直接拼接SQL
   - 添加SQL注入检测和防护机制

3. **权限控制**:
   - 加强apiName参数的权限验证
   - 实现细粒度的资源访问控制
   - 添加操作审计日志

## 结论

jshERP系统中存在多个严重的SQL注入漏洞，主要原因是直接拼接用户输入构建SQL语句。虽然部分查询使用了MyBatis的参数化查询，但系统整体上缺乏统一的输入验证和SQL注入防护机制。

建议立即修复Critical级别的SINK-002漏洞，并尽快修复其他High级别漏洞。同时，从架构层面改进查询安全机制，实现更全面的安全防护。
