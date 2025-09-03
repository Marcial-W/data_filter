# 数据去重过滤器项目

这是一个基于Python的数据去重处理项目，支持多种存储方式实现数据过滤和去重功能。

## 功能特性

- **多种存储方式**：支持内存、Redis、MySQL、布隆过滤器四种存储方式
- **连接池优化**：MySQL和Redis都使用连接池，提高性能
- **配置管理**：统一的配置文件管理，支持环境变量
- **异常处理**：完善的错误处理和日志记录
- **统计信息**：提供数据统计和性能监控
- **向后兼容**：保持原有API的兼容性
- **模块化设计**：清晰的代码结构，易于扩展和维护
- **Docker支持**：提供完整的Docker部署方案
- **请求调度器**：新增RequestSchedule模块，支持请求去重和队列管理

## 项目结构

```
data_process/
├── demo/                      # 演示文件
│   ├── test_bloom_filter_demo.py
│   ├── test_memory_filter_demo.py
│   ├── test_mysql_filter_demo.py
│   ├── test_redis_filter_demo.py
│   └── test_redis_queue_demo.py      # 新增：redis 队列演示
├── docker_config/             # Docker配置
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   ├── mysql_data/
│   ├── redis_data/
│   └── redis_bloomfilter_data/
├── redis_queue/               # Redis 队列模块
│   ├── __init__.py
│   ├── base.py
│   ├── fifo_redis_queue.py
│   ├── lifo_redis_queue.py
│   ├── priority_redis_queue.py
│   ├── redis_distributed_lock.py
│   └── config.py              # 新增：统一配置
├── request_manage/
│   ├── __init__.py
│   ├── request.py
│   ├── request_filter/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── data_filter/
│           ├── __init__.py
│           ├── bloomfilter.py
│           ├── memory_filter.py
│           ├── mysql_filter.py
│           └── redis_filter.py
├── test/                      # 测试文件
│   ├── test_bloom_filter.py
│   ├── test_final_verification.py
│   ├── test_improvements.py
│   ├── test_mysql_filter.py
│   ├── test_password_diagnosis.py
│   ├── test_redis_connection.py
│   ├── test_redis_filter.py
│   ├── test_redis_queue_priority.py   # 新增：redis 优先队列测试
│   └── test_request_filter_integration.py
├── requirements.txt
└── README.md
```

## 安装依赖

### 快速安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或仅安装核心依赖
pip install redis sqlalchemy pymysql
```

### 可选依赖（用于开发）

```bash
pip install pytest  # 单元测试
pip install black   # 代码格式化
pip install flake8  # 代码检查
pip install python-dotenv  # 环境变量管理
```

### 环境要求

- Python 3.7+
- MySQL 5.7+ 或 MySQL 8.0+
- Redis 5.0+
- Docker（可选，用于容器化部署）

## 配置说明

### 1. 环境变量配置

复制 `env_example.txt` 为 `.env` 文件，并根据需要修改配置：

```bash
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=data1

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

### 2. 代码中使用配置

```python
from request_manage.utils.config import config

# 获取MySQL连接URL
mysql_url = config.get_mysql_url()

# 获取Redis配置
redis_config = config.get_redis_config()

# 获取MySQL连接池配置
pool_config = config.get_mysql_pool_config()

# 打印当前配置
config.print_config()
```

### 3. 配置优先级

1. **代码参数**：构造函数中的参数优先级最高
2. **环境变量**：从系统环境变量读取
3. **默认配置**：内置的默认值

```python
# 示例：使用自定义配置
filter = RedisFilter(
    redis_host='192.168.1.100',
    redis_port=6380,
    redis_db=1,
    redis_key='custom_filter'
)
```

## 使用方法

### 1. 内存过滤器（适合小数据量）

```python
from request_manage.utils.data_filter import MemoryFilter

filter = MemoryFilter()
data = ['111', '222', '111', '333']

saved_count = 0
existing_count = 0

for item in data:
   if filter.is_exist(item):
      print(f"'{item}' 已存在")
      existing_count += 1
   else:
      filter.save_data(item)
      print(f"'{item}' 保存成功")
      saved_count += 1

print(f"新增数据: {saved_count} 条")
print(f"重复数据: {existing_count} 条")

# 获取统计信息
stats = filter.get_stats()
print(f"统计信息: {stats}")

# 清空数据（可选）
# filter.clear_all()
```

### 2. Redis过滤器（适合分布式环境）

```python
from request_manage.utils.data_filter import RedisFilter

# 使用配置文件
filter = RedisFilter()

# 或自定义配置
filter = RedisFilter(
   redis_host='127.0.0.1',
   redis_port=6379,
   redis_db=0,
   redis_key='my_filter'
)

data = ['111', '222', '111', '333']

saved_count = 0
existing_count = 0

for item in data:
   if filter.is_exist(item):
      print(f"'{item}' 已存在")
      existing_count += 1
   else:
      result = filter.save_data(item)
      if result == 1:
         print(f"'{item}' 保存成功")
         saved_count += 1
      else:
         print(f"'{item}' 保存失败")
         existing_count += 1

print(f"新增数据: {saved_count} 条")
print(f"重复数据: {existing_count} 条")

# 获取统计信息
stats = filter.get_stats()
print(f"统计信息: {stats}")

# 关闭连接
filter.close_connection()
```

### 3. MySQL过滤器（适合大数据量）

```python
from request_manage.utils.data_filter import MySQLFilter

# 使用配置文件
filter = MySQLFilter()

# 或自定义配置
filter = MySQLFilter('mysql+pymysql://user:pass@host:port/db')

data = ['111', '222', '111', '333']

saved_count = 0
existing_count = 0

for item in data:
   if filter.is_exist(item):
      print(f"'{item}' 已存在")
      existing_count += 1
   else:
      result = filter.save_data(item)
      if result == 1:
         print(f"'{item}' 保存成功")
         saved_count += 1
      else:
         print(f"'{item}' 保存失败")
         existing_count += 1

print(f"新增数据: {saved_count} 条")
print(f"重复数据: {existing_count} 条")

# 获取统计信息
stats = filter.get_stats()
print(f"统计信息: {stats}")

# 关闭连接
MySQLFilter.close_connections()
```

### 4. 布隆过滤器（适合超大数据量，可能有误判）

```python
from request_manage.utils.data_filter import BloomFilter

# 使用配置文件
bf = BloomFilter()

# 或自定义配置
bf = BloomFilter(
   redis_host='127.0.0.1',
   redis_port=6379,
   redis_db=1,
   redis_key='bloom_filter'
)

data = ['111', '222', '111', '333']

saved_count = 0
existing_count = 0

for item in data:
   if bf.is_exist(item):
      print(f"'{item}' 已存在")
      existing_count += 1
   else:
      result = bf.save_data(item)
      if result:
         print(f"'{item}' 保存成功")
         saved_count += 1
      else:
         print(f"'{item}' 保存失败")
         existing_count += 1

print(f"新增数据: {saved_count} 条")
print(f"重复数据: {existing_count} 条")

# 获取统计信息
stats = bf.get_stats()
print(f"统计信息: {stats}")

# 测试误判情况
test_items = ['new_item_1', 'new_item_2', 'new_item_3']
for item in test_items:
   if bf.is_exist(item):
      print(f"'{item}' 可能存在（可能是误判）")
   else:
      print(f"'{item}' 确定不存在")

# 关闭连接
bf.close_connection()
```

## Docker部署

### 快速启动

```bash
# 进入Docker配置目录
cd docker_config

# 启动所有服务（MySQL + Redis）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 环境变量配置

在Docker环境中，可以通过环境变量配置：

```bash
# MySQL配置
export MYSQL_HOST=mysql8
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=123456
export MYSQL_DATABASE=data1

# Redis配置
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_DB=0
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 测试和演示

### 运行测试

```bash
# Redis过滤器测试
python test/test_redis_filter.py

# MySQL过滤器测试
python test/test_mysql_filter.py

# 布隆过滤器测试
python test/test_bloom_filter.py

# 请求过滤器集成测试
python test/test_request_filter_integration.py

# 改进功能测试
python test/test_improvements.py

# Redis 队列（优先队列）测试  # 新增
python test/test_redis_queue_priority.py
```

### 测试文件说明

- **test_redis_filter.py**: Redis过滤器功能测试，包括连接池、性能、错误处理等
- **test_mysql_filter.py**: MySQL过滤器功能测试，包括连接池、性能、错误处理等  
- **test_bloom_filter.py**: 布隆过滤器功能测试，包括误判率、性能、参数调优等
- **test_request_filter_integration.py**: 请求过滤器集成测试，测试不同过滤器类型的兼容性和集成功能
- **test_improvements.py**: 改进功能测试，验证代码优化后的新特性
- **test_improvements.py**: 改进功能测试，验证代码优化后的新特性
```

### 运行演示程序

```bash
# Redis过滤器演示
python demo/test_redis_filter_demo.py

# 内存过滤器演示
python demo/test_memory_filter_demo.py

# MySQL过滤器演示
python demo/test_mysql_filter_demo.py

# 布隆过滤器演示
python demo/test_bloom_filter_demo.py

# Redis 队列演示  # 新增
python demo/test_redis_queue_demo.py
```

### 批量运行所有演示

```bash
# 在项目根目录下运行
for demo in demo/*_demo.py; do
    echo "运行演示: $demo"
    python "$demo"
    echo "------------------------"
done
```

## 性能优化

### MySQL连接池配置

```python
# 在config.py中调整连接池参数
MYSQL_POOL_SIZE = 10          # 连接池大小
MYSQL_MAX_OVERFLOW = 20       # 最大溢出连接数
MYSQL_POOL_TIMEOUT = 30       # 连接超时时间
MYSQL_POOL_RECYCLE = 3600     # 连接回收时间
```

### Redis连接池配置

Redis连接池在代码中已优化，支持：
- 连接复用
- 超时重试
- 自动解码响应

### 性能对比

| 过滤器类型 | 适用场景 | 内存占用 | 查询速度 | 持久化 | 误判率 |
|-----------|---------|---------|---------|--------|--------|
| 内存过滤器 | 小数据量 | 高 | 最快 | 否 | 0% |
| Redis过滤器 | 分布式环境 | 中等 | 快 | 是 | 0% |
| MySQL过滤器 | 大数据量 | 低 | 中等 | 是 | 0% |
| 布隆过滤器 | 超大数据量 | 最低 | 最快 | 是 | 有误判 |

### 选择建议

- **小数据量（< 1万条）**：使用内存过滤器
- **分布式环境**：使用Redis过滤器
- **大数据量（> 100万条）**：使用MySQL过滤器
- **超大数据量（> 1亿条）**：使用布隆过滤器

## 新增功能

### 1. 统计信息

所有过滤器都支持获取统计信息：

```python
stats = filter.get_stats()
print(f"总记录数: {stats['total_records']}")

# 不同过滤器的统计信息格式
# 内存过滤器: {'total_records': 100, 'storage_type': 'memory_set'}
# Redis过滤器: {'total_records': 100, 'redis_key': 'filter', 'redis_db': 0}
# MySQL过滤器: {'total_records': 100, 'table_name': 'filter'}
# 布隆过滤器: {'total_records': 100, 'bit_array_size': 1000000, 'hash_count': 7}
```

### 2. 数据清理

```python
# 清空所有数据（谨慎使用）
success = filter.clear_all()

# 检查清空结果
if success:
    print("数据清空成功")
else:
    print("数据清空失败")
```

### 3. 连接管理

```python
# 关闭连接
filter.close_connection()  # Redis和布隆过滤器
MySQLFilter.close_connections()  # MySQL

# 检查连接状态
try:
    stats = filter.get_stats()
    print("连接正常")
except Exception as e:
    print(f"连接异常: {e}")
```

### 4. 批量操作

```python
# 批量检查数据是否存在
data_list = ['item1', 'item2', 'item3', 'item4']
existing_items = []
new_items = []

for item in data_list:
    if filter.is_exist(item):
        existing_items.append(item)
    else:
        new_items.append(item)

print(f"已存在: {len(existing_items)} 条")
print(f"新增: {len(new_items)} 条")
```

## 代码改进记录

### 2025-08-30 代码质量优化

#### 1. 架构设计改进
- **抽象基类支持**: 为`BaseFilter`添加了`ABC`抽象基类支持，强制子类实现关键方法
- **类型提示**: 添加了完整的类型提示，提高代码可读性和IDE支持
- **错误处理**: 增强了异常处理机制，提供更友好的错误信息

#### 2. 性能优化
- **内存缓存**: `RequestFilter`添加了内存缓存机制，减少重复计算
- **连接池缓存**: `get_filter_class`函数添加了类缓存，避免重复导入
- **数据清理**: 内存过滤器添加了大小限制和自动清理机制

#### 3. 功能增强
- **属性访问器**: `Request`类使用属性装饰器，提供更好的封装
- **统计信息**: 所有过滤器都支持统一的统计信息接口
- **参数验证**: 增强了参数类型和格式验证

#### 4. 代码规范
- **注释优化**: 统一了注释格式，所有注释都在代码右侧
- **命名规范**: 修复了文件名不一致问题（`memery_filter.py` → `memory_filter.py`）
- **文档完善**: 添加了详细的文档字符串和类型注解

## 注意事项

1. **数据安全**：`clear_all()` 方法会清空所有数据，请谨慎使用
2. **连接管理**：程序结束时记得关闭数据库连接
3. **并发安全**：MySQL过滤器已处理并发冲突
4. **性能考虑**：根据数据量选择合适的过滤器类型
5. **配置优先级**：代码参数 > 环境变量 > 默认配置
6. **布隆过滤器误判**：布隆过滤器可能存在误判，适用于对准确性要求不高的场景
7. **内存使用**：内存过滤器数据会占用程序内存，大数据量时注意内存使用
8. **网络延迟**：Redis和MySQL过滤器受网络延迟影响，建议在本地或低延迟环境使用

## 故障排除

### MySQL连接问题

1. **检查MySQL服务是否启动**
   ```bash
   # Windows
   net start mysql
   
   # Linux/Mac
   sudo systemctl status mysql
   ```

2. **验证连接参数是否正确**
   ```python
   from request_manage.utils.config import config
   config.print_config()
   ```

3. **确认数据库和表是否存在**
   ```sql
   SHOW DATABASES;
   USE data1;
   SHOW TABLES;
   ```

4. **检查用户权限**
   ```sql
   SHOW GRANTS FOR 'root'@'localhost';
   ```

### Redis连接问题

1. **检查Redis服务是否启动**
   ```bash
   # Windows
   redis-server --version
   
   # Linux/Mac
   redis-cli ping
   ```

2. **验证端口是否正确**
   ```bash
   netstat -an | grep 6379
   ```

3. **确认防火墙设置**
   ```bash
   # Windows
   netsh advfirewall firewall show rule name=all | findstr Redis
   
   # Linux
   sudo ufw status
   ```

4. **检查Redis配置**
   ```bash
   redis-cli config get bind
   redis-cli config get port
   ```

### 布隆过滤器问题

1. **误判率过高**：调整位数组大小和哈希函数数量
2. **内存占用过大**：减少位数组大小
3. **查询速度慢**：检查Redis连接性能

### 性能问题

1. **调整连接池大小**
   ```python
   # 在config.py中调整
   MYSQL_POOL_SIZE = 20  # 增加连接池大小
   ```

2. **检查数据库索引**
   ```sql
   SHOW INDEX FROM filter;
   ```

3. **监控连接数使用情况**
   ```python
   # 获取连接池状态
   stats = filter.get_stats()
   print(f"连接池状态: {stats}")
   ```

4. **考虑使用批量操作**
   ```python
   # 批量处理数据
   batch_size = 1000
   for i in range(0, len(data), batch_size):
       batch = data[i:i+batch_size]
       # 处理批次数据
   ```

## 更新日志

### v2.1.0 (当前版本)
- 添加布隆过滤器支持
- 优化项目结构，分离demo和test文件夹
- 增强内存过滤器功能，添加统计和清理方法
- 完善文档，添加详细的使用说明和故障排除
- 统一所有过滤器的API接口
- 添加性能对比和选择建议

### v2.0.0
- 添加配置文件管理
- 优化MySQL连接池
- 增强异常处理
- 添加统计功能
- 支持环境变量配置

### v1.0.0
- 基础过滤器功能
- 支持内存、Redis、MySQL存储
- 基本去重功能

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd data_process
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行测试**
   ```bash
   python -m pytest test/
   ```

### 代码规范

- 使用Python 3.7+语法
- 遵循PEP 8代码风格
- 添加适当的类型注解
- 编写详细的文档字符串

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至：2823709089@qq.com

---

**感谢使用数据去重过滤器项目！** 🚀

## redis_queue 队列模块（配置与用法）  # 新增

- 位置：`redis_queue/`  # 目录
- 配置：`redis_queue/config.py`  # 统一配置
- 工厂：`redis_queue.get_redis_queue_cls(queue_type)`  # 获取类
- 支持类型：`fifo`、`lifo`、`priority`  # 队列种类

### 配置文件

```python
# redis_queue/config.py  # 关键项
CONFIG={
    'host':'localhost','port':6379,'db':0,'password':1234567,'decode_responses':True,
    'cluster_nodes':None,  # [{'host':'10.0.0.1','port':6379}, ...]
    'queue_name_default':'redis_queue','priority_queue_name':'priority_redis_queue',
    'use_lock':True,'lock_name':'redis_queue_lock','lock_ttl':5,
}
```

- 覆盖方式：实例化时传参优先级最高，未传则读取 `CONFIG`  # 优先级

### 使用示例

```python
from redis_queue import get_redis_queue_cls

# FIFO 队列（左出右入）
fifo = get_redis_queue_cls('fifo')(name='fifo_q')
fifo.put({'k':1})
print(fifo.get())

# LIFO 队列（栈）
lifo = get_redis_queue_cls('lifo')(name='lifo_q')
lifo.put({'k':1})
print(lifo.get())

# Priority 队列（zset，权重越大越先出）
pq = get_redis_queue_cls('priority')()
pq.put({'taskA':10,'taskB':20})
print(pq.get())  # 返回列表，成员值在 [0]
```

### 集群模式

```python
from redis_queue import get_redis_queue_cls
from redis_queue.config import CONFIG

CONFIG['cluster_nodes']=[{'host':'10.0.0.1','port':6379},{'host':'10.0.0.2','port':6379}]  # 开启集群
pq = get_redis_queue_cls('priority')()  # 自动走 RedisCluster
```

### 分布式锁（仅 priority 队列可选）

- 开关：`CONFIG['use_lock']=True/False`  # 是否使用锁
- 锁名/TTL：`CONFIG['lock_name']`，`CONFIG['lock_ttl']`  # 参数

### 注意事项

- `priority` 的 `get()` 返回列表，如需直接值：`pq.get()[0]`  # 返回值
- 默认 `password=1234567`，如果无密码请置为 `None` 或实例化传参覆盖  # 认证
- `__init__.py` 的队列映射：`fifo/lifo/priority`，不要使用旧的 `fifo_queue`  # 映射
