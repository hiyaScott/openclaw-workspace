---
name: task-scheduler
description: 任务调度与自动化流程管理，涵盖Cron定时任务、事件驱动调度、工作流编排、状态监控与异常处理。实现从简单定时任务到复杂自动化流水线的全面掌控。
---

# 任务调度

## 概述

任务调度是自动化系统的核心，通过预设规则自动触发、执行和监控任务。从简单的定时备份到复杂的CI/CD流水线，任务调度确保系统按预期可靠运行。

## 核心能力

### 1. Cron 定时任务

**Cron表达式格式**：
```
* * * * *
│ │ │ │ │
│ │ │ │ └── 星期 (0-7, 0和7都是周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

**常用表达式**：

| 任务 | Cron表达式 |
|------|-----------|
| 每分钟 | `* * * * *` |
| 每小时 | `0 * * * *` |
| 每天凌晨2点 | `0 2 * * *` |
| 每周一9点 | `0 9 * * 1` |
| 每月1日 | `0 0 1 * *` |

**Linux Cron配置**：
```bash
# 编辑crontab
crontab -e

# 示例任务
0 2 * * * /path/to/backup.sh          # 每天2点备份
*/15 * * * * /path/to/monitor.sh      # 每15分钟监控
0 9 * * 1-5 /path/to/report.sh        # 工作日9点报告
```

### 2. 事件驱动调度

**触发器类型**：

| 类型 | 触发条件 | 适用场景 |
|------|----------|----------|
| **File Watch** | 文件变更 | 自动构建、同步 |
| **Webhook** | HTTP请求 | CI/CD触发 |
| **Message Queue** | 消息到达 | 异步处理 |
| **Database Trigger** | 数据变更 | 数据同步 |

**Python watchdog示例**：
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"File changed: {event.src_path}")
            # 触发重新加载或构建
            rebuild_application()

observer = Observer()
observer.schedule(FileChangeHandler(), path='./src', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### 3. 工作流编排

**复杂工作流设计**：
```yaml
# 工作流定义示例
workflow:
  name: data-pipeline
  
  tasks:
    - name: extract
      command: python extract_data.py
      
    - name: transform
      command: python transform.py
      depends_on: [extract]
      
    - name: load
      command: python load_to_db.py
      depends_on: [transform]
      
    - name: notify
      command: python send_notification.py
      depends_on: [load]
      condition: always  # 无论成功失败都执行
```

### 4. 状态监控与告警

**健康检查模式**：
```python
import time
from datetime import datetime, timedelta

class TaskMonitor:
    def __init__(self):
        self.tasks = {}
    
    def register_task(self, task_id, expected_interval):
        """注册任务监控"""
        self.tasks[task_id] = {
            'last_run': None,
            'expected_interval': expected_interval,
            'status': 'unknown'
        }
    
    def heartbeat(self, task_id):
        """任务心跳上报"""
        if task_id in self.tasks:
            self.tasks[task_id]['last_run'] = datetime.now()
            self.tasks[task_id]['status'] = 'healthy'
    
    def check_health(self):
        """检查所有任务健康状态"""
        now = datetime.now()
        alerts = []
        
        for task_id, info in self.tasks.items():
            if info['last_run'] is None:
                alerts.append(f"Task {task_id} has never run")
            elif now - info['last_run'] > info['expected_interval']:
                alerts.append(f"Task {task_id} is overdue")
        
        return alerts
```

## 调度策略

### 优先级管理

| 优先级 | 说明 | 示例 |
|--------|------|------|
| **Critical** | 系统关键任务 | 数据备份、安全扫描 |
| **High** | 业务重要任务 | 报表生成、数据同步 |
| **Normal** | 常规任务 | 日志清理、缓存刷新 |
| **Low** | 可延迟任务 | 数据分析、优化任务 |

### 失败处理

**重试策略**：
```python
from functools import wraps
import time

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (attempt + 1))  # 指数退避
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def fetch_data():
    # 可能失败的操作
    pass
```

## 工具推荐

| 工具 | 类型 | 适用场景 |
|------|------|----------|
| **Cron** | 系统级 | Linux定时任务 |
| **APScheduler** | Python库 | Python应用内调度 |
| **Celery** | 分布式 | 分布式任务队列 |
| **Airflow** | 工作流 | 复杂数据管道 |
| **n8n** | 可视化 | 低代码自动化 |

## 最佳实践

1. **幂等性设计** - 任务可安全重复执行
2. **超时控制** - 防止任务无限运行
3. **资源限制** - CPU/内存使用上限
4. **日志记录** - 详细的执行记录
5. **优雅关闭** - 支持任务中断和恢复

## 参考资源

- [Cron Best Practices](https://blog.shalvah.me/posts/cron-best-practices)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Linux Cron Howto](https://linux.die.net/man/8/cron)
