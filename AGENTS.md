\## Project Overview
这是一个 Python 数据分析项目，用于管理猫咪的CRM系统的搭建、建模和报表生成。

核心目标：
\- 保持代码可维护
\- 优先可读性
\- 避免过度抽象

\---

\## Tech Stack
\- Python 3.9
\- Pandas
\- FastAPI
\- MySQL
\- Redis
\- Docker
\- Flask

\---

\## Code Style
必须遵守：

\- 使用 type hints
\- 函数长度 <= 50 行
\- 一个函数只做一件事
\- 优先 early return
\- 不允许超过 3 层嵌套
\- 日志统一使用 logging，不允许 print
\- 所有注释必须中文
\- 所有变量名必须英文

\---

\## Architecture Rules

目录职责：

src/api        → 接口层
src/service    → 业务层
src/repository → 数据访问层
src/models     → 数据模型
src/utils      → 工具函数

规则：

\- API 层不能直接访问数据库
\- 必须经过 service 层
\- repository 层禁止业务逻辑

\---

\## Database Rules

修改数据库前必须：

1. 先检查 migration
2. 输出变更影响分析
3. 不允许直接 drop column


\---

\## Testing Rules

修改代码后必须运行：

pytest -v

如果改动：
\- API → 测接口测试
\- SQL → 测集成测试
\- 核心算法 → 测边界条件

覆盖率要求：

\>= 80%

\---

\## Git Rules

提交前：

1. 运行 lint
2. 运行 test
3. 检查 breaking changes


commit message:

feat:
fix:
refactor:
docs:

\---

\## Security Rules

禁止：

\- 输出 .env 内容
\- 修改生产配置
\- 提交密钥
\- 删除数据库

涉及：
config/
.env
prod/

必须先询问。

\---

\## Response Rules

每次修改代码时：

必须输出：

1. 修改文件列表
2. 修改原因
3. 风险点
4. 测试建议


禁止直接 silent modify。


通用配置：
\- 生产服务器ip地址 : 67.219.106.150
\- 项目使用域名:xui6.bbbus.top/cat
\- 生产服务器中docker使用mysql数据库

开发理念：
\- Saas服务
\- 微服务架构
