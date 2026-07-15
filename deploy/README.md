# Cat_Sys CRM 部署指南

## 环境说明

| 环境 | 服务器 | IP | 域名 | 说明 |
|------|--------|-----|------|------|
| 开发 | Rocky Linux 9 VM | 10.0.0.120 | 无 | 手动部署学习K3s |
| 生产 | 生产服务器 | 67.219.106.150 | xui6.bbbus.top/cat | 正式运营 |

## Rocky Linux 9 前置准备

```bash
# 1. 安装 Docker
dnf install -y dnf-utils
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io
systemctl start docker && systemctl enable docker

# 配置 Docker 国内镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn"
  ]
}
EOF
systemctl daemon-reload && systemctl restart docker

# 2. 安装 K3s
curl -sfL https://get.k3s.io | sh -
chmod 644 /etc/rancher/k3s/k3s.yaml

# 3. 防火墙放行 NodePort
firewall-cmd --zone=public --add-port=30002/tcp --permanent
firewall-cmd --reload

# 4. 验证
kubectl get nodes
```

## 构建镜像

```bash
cd /opt/catsys
./deploy/scripts/build-all.sh
```

构建脚本会依次：
1. 构建 7 个微服务镜像（api-gateway + 6 个 service）
2. 自动导入 K3s 的 containerd

## 部署到 K3s

```bash
cd /opt/catsys
./deploy/scripts/deploy-all.sh
```

部署顺序：命名空间 -> ConfigMap -> Secrets -> MySQL -> Redis -> 7 个微服务

## 验证

```bash
# 查看所有资源
kubectl get all -n cat-sys

# 查看 Pod 状态
kubectl get pods -n cat-sys -w

# 测试 API 网关
curl http://10.0.0.120:30002/cat/health

# 注册商家
curl -X POST http://10.0.0.120:30002/cat/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"phone":"13800000001","password":"admin123","business_name":"测试猫舍","contact_person":"张三"}'

# 登录
curl -X POST http://10.0.0.120:30002/cat/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"phone":"13800000001","password":"admin123"}'
```

## 查看日志

```bash
kubectl logs -n cat-sys -l app=api-gateway --tail=50
kubectl logs -n cat-sys -l app=user-service -f
kubectl logs -n cat-sys -l app=mysql
```

## 常见异常排查

| 异常现象 | 原因 | 解决 |
|---------|------|------|
| Pod ImagePullBackOff | 镜像未导入 containerd | 重跑 build-all.sh |
| MySQL CrashLoopBackOff | 数据卷权限 | kubectl delete pvc -n cat-sys mysql-pvc 重建 |
| API 返回 503 | 内部服务未就绪 | kubectl get pods -n cat-sys 检查 |
| curl 连不上 30002 | 防火墙未放行 | firewall-cmd --add-port=30002/tcp |
| ModuleNotFoundError: No module named 'src' | 镜像缺共享代码 | 确认 Dockerfile 有 COPY src/ |
| Docker pull 超时 | 镜像源被墙 | 配置 registry-mirrors |
| kubectl 命令报权限错 | kubeconfig 权限 | chmod 644 /etc/rancher/k3s/k3s.yaml |

## 切换环境

```bash
# 开发 VM
cp config/development.env .env
./deploy/scripts/switch-env.sh dev

# 生产
cp config/production.env .env
./deploy/scripts/switch-env.sh prod
```

## 附录：服务端口对照

| 服务 | 内部端口 | 外部访问 |
|------|---------|---------|
| api-gateway | 9002 | 10.0.0.120:30002 |
| user-service | 5001 | 内部 ClusterIP |
| merchant-service | 5002 | 内部 ClusterIP |
| cat-service | 5003 | 内部 ClusterIP |
| crm-service | 5004 | 内部 ClusterIP |
| finance-service | 5005 | 内部 ClusterIP |
| dashboard-service | 5006 | 内部 ClusterIP |
| MySQL | 3306 | 内部 ClusterIP |
| Redis | 6379 | 内部 ClusterIP |
