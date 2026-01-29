# jshERP项目SQL注入漏洞分析报告

## 漏洞概述

通过对 `/Users/lousix/sec/ctf/AAA/2023/xhlj2024/jshERP/jshERP-boot` 项目的分析，发现了多个潜在的SQL注入漏洞，主要集中在MyBatis XML映射文件中使用 `${}` 占位符的地方。

## 漏洞详情

### 1. OrderUtils类中的SQL注入漏洞

**位置**: `src/main/java/com/jsh/erp/utils/OrderUtils.java`

**漏洞描述**:

- `getOrderString`方法 (行14-31)
- `getJoinTablesOrderString`方法 (行33-41)
- `getOrderString`重载方法 (行52-68)

**漏洞代码**:

```java
public static String getOrderString(String orders) {
    if (StringUtil.isNotEmpty(orders)) {
        String[] splits = orders.split(Constants.SPLIT);
        if (splits.length == 2) {
            String column = ColumnPropertyUtil.propertyToColumn(splits[0]);
            if (column.equals("audit_status")) {
                return "IF(`audit_status`=3,-1,`audit_status`) " + splits[1];
            } else if (column.equals("create_time") || column.equals("modify_time")) {
                return column + " " + splits[1];
            } else {
                return "convert(" + column + " using gbk) " + splits[1];
            }
        }
    }
    return "";
}
```

**漏洞分析**:

- 直接使用字符串拼接构造SQL排序语句
- `splits[0]`和`splits[1]`参数未经充分过滤就拼接到SQL中
- 虽然通过`ColumnPropertyUtil.propertyToColumn`进行了一定的转换，但仍可能存在绕过

### 2. MyBatis XML中的SQL注入漏洞

#### 2.1 通用动态SQL注入

**位置**: 所有Mapper XML文件中的动态条件部分

**漏洞描述**: 大量使用`${criterion.condition}`进行动态SQL拼接

**漏洞模式**:

```xml
<if test="criterion.condition != null">
    and ${criterion.condition}
</if>
<if test="criterion.condition != null">
    and ${criterion.condition} #{criterion.value}
</if>
<if test="criterion.condition != null">
    and ${criterion.condition} #{criterion.value} and #{criterion.secondValue}
</if>
```

**受影响的文件包括**:

- `AccountHeadMapper.xml`
- `DepotHeadMapper.xml`
- `PersonMapper.xml`
- `OrgaUserRelMapper.xml`
- `UnitMapper.xml`
- `InOutItemMapper.xml`
- `RoleMapper.xml`
- `TenantMapper.xml`
- `MaterialCategoryMapper.xml`
- `DepotMapper.xml`
- `AccountMapper.xml`
- 等多个Mapper文件

#### 2.2 Order by子句注入

**位置**: 多个Mapper XML文件中的order by子句

**漏洞代码**:

```xml
order by ${orderByClause}
```

**受影响的文件**:

- `AccountHeadMapper.xml` (行96)
- `DepotHeadMapper.xml` (行113)
- `PersonMapper.xml` (行85)
- `OrgaUserRelMapper.xml` (行109)
- `UnitMapper.xml` (行91)
- `InOutItemMapper.xml` (行86)
- `RoleMapper.xml` (行88)
- `TenantMapper.xml` (行88)
- `MaterialCategoryMapper.xml` (行90)
- `DepotMapper.xml` (行92)
- `AccountMapper.xml` (行90)
- 等多个文件

## 调用链分析

### 调用链示例1: OrderUtils SQL注入

**Source (输入源)**:

- HTTP请求参数中的排序字段
- 例如: `/depotHead/list?sortColumn=name&sortOrder=asc`

**调用链**:

```
Controller层:
└── DepotHeadController.findInOutDetail() (行99-155)
    └── Service层:
        └── DepotHeadService.findInOutDetail()
            └── Mapper层:
                └── DepotHeadMapperEx.findInOutDetail()
                    └── OrderUtils.getOrderString() (行14-31)
                        └── 直接字符串拼接构造SQL
                            └── Sink: SQL执行
```

### 调用链示例2: 动态条件SQL注入

**Source (输入源)**:

- 通用查询接口的搜索参数
- 例如: `/commonQuery?apiName=depotHead&search=condition`

**调用链**:

```
Controller层:
└── 通用查询Controller
    └── Service层:
        └── CommonQueryManager.select() (行47-52)
            └── InterfaceContainer.getCommonQuery()
                └── DepotHeadComponent.select() (行28-30)
                    └── DepotHeadService.select()
                        └── Mapper层:
                            └── DepotHeadMapperEx.selectByConditionDepotHead()
                                └── 使用${criterion.condition}直接拼接
                                    └── Sink: SQL执行
```

## Source和Sink点总结

### Source点 (输入源):

1. **HTTP请求参数**:

   - 排序参数 (sortColumn, sortOrder)
   - 搜索条件参数 (search, materialParam, number等)
   - 通用查询参数 (apiName, condition)

2. **配置参数**:
   - 配置文件中的动态SQL片段
   - 数据库列名映射配置

### Sink点 (漏洞触发点):

1. **MyBatis XML中的${}占位符**:

   - 条件判断中的`${criterion.condition}`
   - 排序子句中的`${orderByClause}`

2. **Java代码中的字符串拼接**:
   - OrderUtils类中的字符串拼接
   - 动态SQL构造方法

## 利用方式

### 1. 排序字段注入

攻击者可以通过构造恶意的排序参数来注入SQL：

```
原始请求: /depotHead/list?sortColumn=name&sortOrder=asc
恶意请求: /depotHead/list?sortColumn=name;(SELECT SLEEP(5))&sortOrder=asc
```

### 2. 动态条件注入

通过通用查询接口注入恶意条件：

```
恶意payload: 1=1; DROP TABLE jsh_user; --
```

### 3. Order By子句注入

在order by参数中注入恶意SQL：

```
恶意payload: id) AND (SELECT COUNT(*) FROM information_schema.tables)>0 --
```

## 修复建议

### 1. 立即修复措施

- 将所有`${}`占位符替换为`#{}`占位符
- 对OrderUtils中的字符串拼接进行严格白名单验证
- 增加输入参数的合法性检查

### 2. 长期修复方案

- 使用参数化查询替代字符串拼接
- 实现严格的输入验证和过滤机制
- 进行全面的安全代码审查
- 增加自动化安全测试

### 3. 防御措施

- 部署Web应用防火墙(WAF)
- 实施最小权限原则
- 加强日志监控和异常检测
- 定期进行安全渗透测试

## 风险评估

**风险等级**: 高
**影响范围**: 整个ERP系统
**潜在危害**:

- 数据泄露
- 数据篡改
- 系统权限提升
- 数据库被删除

## 总结

该项目存在多个严重的SQL注入漏洞，主要原因是大量使用不安全的SQL拼接方式。建议立即进行修复，并对整个系统进行全面的安全加固。
