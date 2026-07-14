# Cat_Sys CRM v0.1 — 详细设计文档

> 版本: v0.1
> 状态: 草稿待确认
> 日期: 2026-07-09

---

## 1. 系统架构总览

### 1.1 架构模式：微服务架构

系统拆分为 6 个独立微服务 + 1 个 API 网关，服务间通过内部 HTTP REST 通信。

### 1.2 架构图

```
Clients → api-gateway → user-service / merchant-service / cat-service / crm-service / finance-service / dashboard-service → MySQL (各服务独立) + Redis
```

### 1.3 服务职责矩阵

| 服务 | 端口 | 框架 | 数据库 | 核心职责 |
|------|------|------|--------|---------|
| api-gateway | 9002 | Flask | Redis | 路由转发、JWT 验证、模块开关拦截 |
| user-service | 5001 | FastAPI | MySQL + Redis | 用户注册/登录、员工管理、角色管理 |
| merchant-service | 5002 | FastAPI | MySQL | 商家 CRUD、分店管理、模块开关配置 |
| cat-service | 5003 | FastAPI | MySQL | 猫咪 CRUD、健康记录管理 |
| crm-service | 5004 | FastAPI | MySQL | 客户管理、预订/定金、合同签署 |
| finance-service | 5005 | FastAPI | MySQL | 收支流水、财务报表 |
| dashboard-service | 5006 | FastAPI | MySQL（只读） | 聚合统计、仪表盘数据 |


### 1.5 权限矩阵

| 操作 | 商家主理人 | 店长 | 销售 | 护理员 |
|------|-----------|------|------|--------|
| 查看本分店数据 | 全部商家 | 本分店 | 本分店 | 本分店 |
| 新增/编辑猫咪 | 允许 | 允许 | 允许 | 允许 |
| 修改猫咪售价 | 允许 | 允许 | 允许 | 允许 |
| 新增/编辑客户 | 允许 | 允许 | 允许 | 仅查看 |
| 创建预订/合同 | 允许 | 允许 | 允许 | 禁止 |
| 新增健康/洗护记录 | 允许 | 允许 | 仅查看 | 允许 |
| 创建/删除分店 | 允许 | 禁止 | 禁止 | 禁止 |
| 添加/禁用员工 | 允许 | 禁止 | 禁止 | 禁止 |
| 查看财务报表 | 允许 | 允许 | 禁止 | 禁止 |
| 查看审计日志 | 允许 | 本分店 | 禁止 | 禁止 |

> 注：超级管理员拥有全平台所有权限，不受此表限制。

### 1.4 请求链路

客户端 → xui6.bbbus.top/cat/api/* → api-gateway（URL_PREFIX=/cat 剥离前缀 + 验证 JWT + 校验模块开关 + 注入 merchant_id/branch_id）→ 下游服务 → 返回响应

---

## 2. 功能模块开关机制

### 2.1 模块目录

| 编码 | 名称 | 类型 |
|------|------|------|
| cat_mgmt | 猫咪管理 | basic |
| customer_mgmt | 客户管理 | basic |
| branch_mgmt | 分店管理 | basic |
| employee_mgmt | 员工管理 | basic |
| dashboard | 基础仪表盘 | basic |
| account | 账号与权限 | basic |
| sales | 销售管理 | advanced |
| health_pro | 健康管理 Pro | advanced |
| contract | 合同与证书 | advanced |
| finance | 财务报表 | advanced |
| bulk_ops | 批量导入导出 | advanced |
| api_access | API 接口 | advanced |
| auto_followup | 客户自动跟进 | advanced |

### 2.2 开关机制

超级管理员在开发者管理后台 → 进入商家详情 → 模块配置页 → 勾选/取消高级模块 → 保存到 MerchantModule 表 → 同步到 Redis。

运行时：API 网关从 Token 中提取该商家的已开通模块列表，判断请求路径对应的模块是否已开通，未开通返回 403。

基础模块强制开通，超管无法关闭。

### 2.3 API 与模块映射

| 路由前缀 | 模块编码 |
|----------|---------|
| /api/auth/* | account |
| /api/users/* | account |
| /api/employees/* | employee_mgmt |
| /api/merchants/* | （超管/商家专用，不拦截） |
| /api/branches/* | branch_mgmt |
| /api/modules/* | （超管专用，不拦截） |
| /api/cats/* | cat_mgmt |
| /api/health/* | health_pro |
| /api/customers/* | customer_mgmt |
| /api/sales/* | sales |
| /api/contracts/* | contract |
| /api/followup/* | auto_followup |
| /api/finance/* | finance |
| /api/dashboard/* | dashboard |

---

## 3. 数据模型详细设计

### 3.1 全局约定

所有业务表（非系统表）统一包含：id (PK), merchant_id (FK, NOT NULL), branch_id (FK, NOT NULL), created_at, updated_at, updated_by (INT, FK users.id，最后操作人，前端展示用)。

### 3.2 表结构

**users** — 统一用户表 (user_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| username | VARCHAR(50) | UNIQUE NOT NULL | 登录名 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| phone | VARCHAR(20) | UNIQUE | 手机号 |
| email | VARCHAR(100) | | 邮箱 |
| real_name | VARCHAR(50) | NOT NULL | 真实姓名 |
| user_type | ENUM | NOT NULL | super_admin / merchant_owner / branch_employee |
| status | ENUM | NOT NULL DEFAULT 'active' | active / disabled |
| last_login | DATETIME | | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**employees** — 员工信息表 (user_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| user_id | INT | FK users.id NOT NULL | |
| merchant_id | INT | FK merchants.id NOT NULL | |
| current_branch_id | INT | FK branches.id | 当前工作分店 |
| role_code | ENUM | NOT NULL | manager / sales / care_staff |
| job_title | VARCHAR(50) | | 职称 |
| status | ENUM | NOT NULL DEFAULT 'active' | active / disabled |
| hired_at | DATETIME | NOT NULL | |
| left_at | DATETIME | | 离职时间 |

**merchants** — 商家表 (merchant_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| owner_user_id | INT | FK users.id NOT NULL | |
| business_name | VARCHAR(100) | NOT NULL | 猫舍名称 |
| business_license | VARCHAR(50) | | 营业执照 |
| contact_person | VARCHAR(50) | NOT NULL | |
| contact_phone | VARCHAR(20) | NOT NULL | |
| contact_email | VARCHAR(100) | | |
| address | VARCHAR(255) | | |
| logo_url | VARCHAR(255) | | |
| status | ENUM | NOT NULL DEFAULT 'active' | active / suspended / expired / deleted |
| expiry_date | DATE | | |
| registered_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**branches** — 分店表 (merchant_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK merchants.id NOT NULL | |
| name | VARCHAR(100) | NOT NULL | 分店名称 |
| address | VARCHAR(255) | | |
| contact_phone | VARCHAR(20) | | |
| status | ENUM | NOT NULL DEFAULT 'active' | active / closed |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**modules** — 模块目录表 (merchant_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| code | VARCHAR(50) | UNIQUE NOT NULL | 编码 |
| name | VARCHAR(50) | NOT NULL | 中文名称 |
| module_type | ENUM | NOT NULL | basic / advanced |
| description | VARCHAR(255) | | |
| sort_order | INT | DEFAULT 0 | |
| is_active | TINYINT | DEFAULT 1 | |

**merchant_modules** — 商家模块开通表 (merchant_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK merchants.id NOT NULL | |
| module_code | VARCHAR(50) | FK modules.code NOT NULL | |
| is_enabled | TINYINT | DEFAULT 1 | |
| enabled_at | DATETIME | | |
| disabled_at | DATETIME | | |

**cats** — 猫咪表 (cat_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| name | VARCHAR(50) | NOT NULL | |
| breed | VARCHAR(50) | | 品种 |
| color | VARCHAR(50) | | 毛色 |
| gender | ENUM | | male / female |
| birth_date | DATE | | |
| microchip_number | VARCHAR(50) | | 芯片号 |
| pedigree_number | VARCHAR(50) | | 血统证书号 |
| sire_name | VARCHAR(50) | | 父猫名 |
| dam_name | VARCHAR(50) | | 母猫名 |
| status | ENUM | NOT NULL | available / reserved / sold / retired / deceased |
| price | DECIMAL(10,2) | | 售价 |
| photo_urls | TEXT | | JSON 数组 |
| notes | TEXT | | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**health_records** — 健康记录表 (cat_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| cat_id | INT | FK cats.id NOT NULL | |
| record_type | ENUM | NOT NULL | vaccination / deworming / checkup / illness / surgery |
| record_date | DATE | NOT NULL | |
| next_date | DATE | | 下次日期 |
| vaccine_type | VARCHAR(50) | | |
| deworming_type | VARCHAR(50) | | |
| vet_name | VARCHAR(50) | | |
| clinic | VARCHAR(100) | | |
| result | VARCHAR(255) | | |
| attachments | TEXT | | JSON 数组 |
| notes | TEXT | | |
| created_by | INT | FK users.id | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |

**customers** — 客户表 (crm_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| name | VARCHAR(50) | NOT NULL | |
| phone | VARCHAR(20) | | |
| wechat | VARCHAR(50) | | |
| email | VARCHAR(100) | | |
| address | VARCHAR(255) | | |
| source | VARCHAR(50) | | 来源 |
| status | ENUM | NOT NULL | lead / interested / contracted / owner / lost |
| preferred_breeds | VARCHAR(255) | | 偏好品种 |
| preferred_colors | VARCHAR(255) | | 偏好颜色 |
| budget_min | DECIMAL(10,2) | | |
| budget_max | DECIMAL(10,2) | | |
| notes | TEXT | | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**reservations** — 预订表 (crm_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| cat_id | INT | FK cats.id | |
| customer_id | INT | FK customers.id NOT NULL | |
| reservation_date | DATE | NOT NULL | |
| deposit_amount | DECIMAL(10,2) | | |
| total_price | DECIMAL(10,2) | | |
| status | ENUM | NOT NULL | active / deposit_paid / contracted / completed / cancelled |
| notes | TEXT | | |
| created_by | INT | FK users.id | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**contracts** — 合同表 (crm_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| reservation_id | INT | FK reservations.id | |
| customer_id | INT | FK customers.id NOT NULL | |
| cat_id | INT | FK cats.id | |
| contract_number | VARCHAR(50) | UNIQUE NOT NULL | |
| contract_type | ENUM | NOT NULL | pet / breeding |
| total_amount | DECIMAL(10,2) | NOT NULL | |
| deposit_amount | DECIMAL(10,2) | | |
| remaining_amount | DECIMAL(10,2) | | |
| sign_date | DATE | NOT NULL | |
| file_url | VARCHAR(255) | | |
| status | ENUM | NOT NULL | active / fulfilled / terminated |
| notes | TEXT | | |
| created_by | INT | FK users.id | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_at | DATETIME | NOT NULL | |

**followup_tasks** — 跟进任务表 (crm_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| customer_id | INT | FK customers.id NOT NULL | |
| assignee_id | INT | FK users.id | |
| task_type | ENUM | NOT NULL | followup / birthday / checkin / custom |
| title | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| due_date | DATE | | |
| status | ENUM | NOT NULL DEFAULT 'pending' | pending / completed / cancelled |
| completed_at | DATETIME | | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |

**transactions** — 收支流水表 (finance_db)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK AUTO_INCREMENT | |
| merchant_id | INT | FK NOT NULL | |
| branch_id | INT | FK NOT NULL | |
| type | ENUM | NOT NULL | income / expense |
| category | VARCHAR(50) | NOT NULL | 分类 |
| amount | DECIMAL(10,2) | NOT NULL | |
| transaction_date | DATE | NOT NULL | |
| description | VARCHAR(255) | | |
| related_type | VARCHAR(50) | | |
| related_id | INT | | |
| created_by | INT | FK users.id | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |

**operation_logs** — 操作审计日志 (各服务共用结构)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK AUTO_INCREMENT | |
| service_name | VARCHAR(50) | NOT NULL | |
| operator_id | INT | FK users.id | |
| merchant_id | INT | | |
| action_type | VARCHAR(50) | NOT NULL | create / update / delete / login |
| target_type | VARCHAR(50) | NOT NULL | |
| target_id | INT | | |
| detail | TEXT | | JSON |
| ip_address | VARCHAR(45) | | |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| updated_by | INT | FK users.id | 最后操作人，前端展示用 |
| created_at | DATETIME | NOT NULL | |

---

## 4. API 接口设计

### 4.1 规范

- 统一前缀：/api/{path}（外部访问时为 /cat/api/{path}，由 api-gateway 剥离 /cat 前缀后转发）
- 认证：Authorization: Bearer JWT
- 响应格式：{ "code": 0, "data": {...}, "message": "ok" }
- URL 路径前缀（如 /cat）由配置文件控制，迁移服务器或换域名时仅需修改配置文件

### 4.2 核心端点

**user-service (/api/auth/*)**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册商家账号 |
| POST | /api/auth/login | 登录 |
| POST | /api/auth/switch-branch | 切换分店 |
| GET | /api/employees | 员工列表 |
| POST | /api/employees | 添加员工 |
| PUT | /api/employees/{id}/status | 启用/禁用 |

**merchant-service (/api/merchants/*, /api/branches/*)**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/merchants | 商家列表（超管） |
| POST | /api/merchants | 创建商家（超管） |
| PUT | /api/merchants/{id}/status | 停用/启用（超管） |
| PUT | /api/merchants/{id}/expiry | 设置有效期（超管） |
| PUT | /api/merchants/{id}/modules | 配置模块（超管） |
| GET | /api/branches | 分店列表 |
| POST | /api/branches | 创建分店 |
| DELETE | /api/branches/{id} | 删除分店 |

**cat-service (/api/cats/*, /api/health/*)**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/cats | 猫咪列表 |
| POST | /api/cats | 新增猫咪 |
| PUT | /api/cats/{id} | 编辑猫咪 |
| GET | /api/cats/{id} | 猫咪详情 |
| GET | /api/health | 健康记录列表 |
| POST | /api/health | 新增健康记录 |

**crm-service (/api/customers/*, /api/sales/*, /api/contracts/*)**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/customers | 客户列表 |
| POST | /api/customers | 新增客户 |
| GET | /api/sales/reservations | 预订列表 |
| POST | /api/sales/reservations | 创建预订 |
| GET | /api/contracts | 合同列表 |
| POST | /api/contracts | 创建合同 |

---

## 5. 数据隔离方案

### 5.1 隔离层级

- 平台级：超级管理员可查看所有商家（无 merchant_id 过滤）
- 商家级：各商家只能看到自己的数据（WHERE merchant_id = :merchant_id）
- 分店级：员工按当前分店查看对应数据（WHERE branch_id = :current_branch_id）

### 5.2 实现方式

API 网关解析 JWT → 提取 merchant_id / branch_id / role_code → 注入 HTTP 请求头 X-Merchant-Id / X-Branch-Id → 下游服务在 SQLAlchemy 层自动追加 WHERE 条件。

### 5.3 校验规则

| 用户类型 | 写入 merchant_id | 查询范围 | 跨商家 |
|---------|-----------------|---------|--------|
| 超级管理员 | 接口指定 | 全平台 | 允许 |
| 商家主理人 | 强制自己所属 | 仅本商家 | 禁止 |
| 分店员工 | 强制自己所属 | 仅本商家 | 禁止 |

---

## 6. 员工切换分店

### 6.1 Token 结构 (JWT Payload)

{ user_id, merchant_id, current_branch_id, role_code, user_type, enabled_modules: [...], exp }

### 6.2 切换流程

员工登录 → 获取 Token（含 current_branch_id）→ 调用 GET /api/branches 获取商家所有分店 → 选择目标分店 → 调用 POST /api/auth/switch-branch { branch_id } → 返回新 Token（current_branch_id 更新）→ 后续请求使用新 Token。

---

## 7. 开发者管理平台

| 菜单 | 子功能 | 说明 |
|------|--------|------|
| 控制台 | 平台总览 | 商家总数、活跃数、即将到期数 |
| 商家管理 | 商家列表 | 搜索/筛选/分页 |
| 商家管理 | 创建商家 | 填写信息，自动生成主理人账号 |
| 商家管理 | 编辑/停用/删除 | 二次确认 + 密码确认 |
| 商家管理 | 设置有效期 | 修改到期日期 |
| 商家管理 | 模块配置 | 勾选/取消高级模块 |
| 模块管理 | 模块目录 | 编辑模块定义 |
| 系统配置 | 注册/默认配置 | 注册开关、新商家默认值 |
| 审计日志 | 日志查看 | 按条件筛选查看 |

---

## 8. 部署方案

### 8.1 Docker Compose 服务列表

| 服务 | 内部端口 | 外部暴露 | 说明 |
|------|---------|---------|------|
| api-gateway | 9002 | 9002:9002 | 唯一对外入口 |
| user-service | 5001 | 不暴露 | Docker 内部通信 |
| merchant-service | 5002 | 不暴露 | Docker 内部通信 |
| cat-service | 5003 | 不暴露 | Docker 内部通信 |
| crm-service | 5004 | 不暴露 | Docker 内部通信 |
| finance-service | 5005 | 不暴露 | Docker 内部通信 |
| dashboard-service | 5006 | 不暴露 | Docker 内部通信 |
| mysql | 3306 | 不暴露 | 数据持久化 |
| redis | 6379 | 不暴露 | 缓存 |

> 唯一对外入口为 api-gateway 的 9002 端口，所有外部请求通过 http://{host}:9002/cat/api/... 访问。

### 8.2 项目目录结构

```
E:\Project\Cat_Sys\
+ AGENTS.md
+ docker-compose.yml
+ requirements.txt
+ .gitignore              # 排除 .env / __pycache__ / *.pyc
+ config/
   + production.env         # 生产配置（不提交 Git，含密钥）
   + development.env        # 开发配置（示例值，可提交）
   + common.env             # 公共配置（可提交）
+ docs/
   + PRD_v0.1.md
   + DESIGN_v0.1.md
+ api-gateway/
   + Dockerfile
   + requirements.txt
   + app/
       + __init__.py
       + config.py
       + middleware.py
       + routes.py
       + proxy.py
+ services/
   + user-service/
   + merchant-service/
   + cat-service/
   + crm-service/
   + finance-service/
   + dashboard-service/
+ tests/
+ AGENTS.md
+ docker-compose.yml
+ .env.example
+ requirements.txt
+ docs/
   + PRD_v0.1.md
   + DESIGN_v0.1.md
+ api-gateway/
   + Dockerfile
   + requirements.txt
   + app.py
+ services/
   + user-service/
   + merchant-service/
   + cat-service/
   + crm-service/
   + finance-service/
   + dashboard-service/
+ tests/
```

---

## 9. 风险

1. 微服务间 HTTP 调用增加延迟 — v0.1 可接受
2. 各服务独立数据库，跨服务事务困难 — v0.1 避免跨服务事务
3. 网关单点故障 — Docker 可水平扩展
4. Redis 宕机影响模块开关 — 降级查数据库
5. 员工离职数据交接 — v0.1 手动交接

---

## 10. v0.1 不包含

- 繁育管理模块
- 短信通知
- 多语言支持
- 套餐定价与支付
- 消息队列
- 文件上传服务（v0.1 用 URL 字段）
- 前端界面（v0.1 仅提供 REST API）
