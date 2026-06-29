# 分类与标签指南

动态二级分类 + 标签。Agent 在运行时自行判定；同一份报告内保持一致。

## 第一级 — 大领域

| 大领域 | 典型范围 |
|--------|----------|
| Java | 语言、JVM、JDK API |
| Python | 语言、标准库、包管理 |
| Spring | Framework、Boot、Cloud |
| Redis | 命令、持久化、集群 |
| Database | SQL、MySQL、PostgreSQL、ORM |
| Frontend | React、Vue、CSS |
| DevOps | Docker、CI/CD、Linux |
| AI/ML | LLM、RAG、Embedding、Agent |
| Tools | Git、Maven、Cursor、IDE |

选最具体领域：`@Autowired` 用 Spring，语法糖用 Java。

## 第二级 — 子领域

- Java → `并发`、`ArrayList`、`JVM 内存模型`、`泛型`
- Spring → `IOC`、`AOP`、`自动配置`、`Bean 生命周期`
- Redis → `网络模型`、`持久化 RDB/AOF`、`主从复制`

盲区标签取**最深、仍未解决**的子领域。

## 标签 — 问题性质

| 标签 | 适用场景 |
|------|----------|
| 语法问题 | API 用法、编译错误 |
| 概念理解 | 「是什么」、心智模型缺失 |
| 原理知识 | 底层机制 |
| 调试排错 | 异常、行为不符 |
| 架构设计 | 模块边界、设计模式 |
| 工具使用 | IDE、CLI、Cursor |
| 最佳实践 | 惯用法、反模式 |

## 分类规则

1. 每个问题单元统计表一行
2. 同线程分类一致，除非明显换题
3. 盲区按**根因困惑**分类
4. 源码关联优先级：已触达 > 消息提及 > 推断 `(推断)`
