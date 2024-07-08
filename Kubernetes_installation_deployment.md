```bash
#注 用root用户执行
----------------------------------------------------------------------------------------------------
# 1、设置主机名
hostnamectl set-hostname k8s-master
----------------------------------------------------------------------------------------------------
# 2、添加hosts解析
cat >> /etc/hosts << EOF
10.156.112.98 k8s-master
EOF
----------------------------------------------------------------------------------------------------
# 3、同步时间
apt install -y chrony
systemctl restart chrony
systemctl status chrony
systemctl ebable chrony
chronyc sources
----------------------------------------------------------------------------------------------------
# 4.永久关闭swap(需重启系统生效)
swapoff -a  # 临时关闭
sed -i 's/.*swap.*/#&/g' /etc/fstab # 永久关闭
----------------------------------------------------------------------------------------------------
# 5.关闭防火墙、清空iptables规则
ufw disable && ufw status
----------------------------------------------------------------------------------------------------
# 6.加载IPVS模块
apt install ipset ipvsadm -y
cat > /etc/modules-load.d/ipvs.conf << EOF
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack
EOF
modprobe -- nf_conntrack
chmod 755 /etc/modules-load.d/ipvs.conf && bash /etc/modules-load.d/ipvs.conf && lsmod | grep -e ip_vs -e nf_conntrack
----------------------------------------------------------------------------------------------------
# 7、开启br_netfilter、ipv4 路由转发
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
# 设置所需的 sysctl 参数，参数在重新启动后保持不变
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
# 设置所需的 sysctl 参数，参数在重新启动后保持不变
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
----------------------------------------------------------------------------------------------------
# 8.应用 sysctl 参数而不重新启动
sysctl --system

# 查看是否生效
lsmod | grep br_netfilter
lsmod | grep overlay
sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward
# 9、设置资源配置文件
cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 100001
* hard nofile 100002
root soft nofile 100001
root hard nofile 100002
* soft memlock unlimited
* hard memlock unlimited
* soft nproc 254554
* hard nproc 254554
* soft sigpending 254554
* hard sigpending 254554
EOF
grep -vE "^\s*#" /etc/security/limits.conf
 
ulimit -a
----------------------------------------------------------------------------------------------------
# 19.安装 containerd
apt  install containerd  -y
----------------------------------------------------------------------------------------------------
# 10.安装kubernetes
# 安装基础环境
apt-get install -y ca-certificates curl software-properties-common apt-transport-https curl
curl -s https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | sudo apt-key add -
# 执行配置k8s阿里云源  
vim /etc/apt/sources.list.d/kubernetes.list
#加入以下内容
deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-xenial main
# 执行更新
apt-get update -y
#查看kubeadm kubelet kubectl有哪些版本，以及版本安装时的具体名称，例如1.23.6是错误的，要是1.23.6-00
apt-cache madison kubeadm kubelet kubectl
#安装指定版本的kubeadm kubelet kubectl
sudo apt update && \
sudo apt-get -y install kubelet=1.28.2-00 kubeadm=1.28.2-00 kubectl=1.28.2-00    # 安装的时候需要指定版本，否则会安装最新版本，node节点可以不需要安装kubectl
sudo apt-mark hold kubelet kubeadm kubectl        #阻止软件自动更新
systemctl start kubelet 
systemctl enable kubelet

查看安装的情况以及版本
kubectl version --client && kubeadm version
----------------------------------------------------------------------------------------------------
# 11. 配置containerd
mdkir /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# 修改cgroup Driver为systemd
sed -ri 's#SystemdCgroup = false#SystemdCgroup = true#' /etc/containerd/config.toml

# 更改sandbox_image
sed -ri 's#registry.k8s.io\/pause:3.6#registry.aliyuncs.com\/google_containers\/pause:3.9#' /etc/containerd/config.toml

# endpoint位置添加阿里云的镜像源
sed -ri 's#https:\/\/registry-1.docker.io#https:\/\/registry.aliyuncs.com#' /etc/containerd/config.toml

systemctl daemon-reload && systemctl restart containerd && systemctl enable containerd 
----------------------------------------------------------------------------------------------------
# 12.#设置crictl
cat << EOF >> /etc/crictl.yaml
runtime-endpoint: unix:///var/run/containerd/containerd.sock
image-endpoint: unix:///var/run/containerd/containerd.sock
timeout: 10
debug: false
EOF
----------------------------------------------------------------------------------------------------
# 13.初始化集群文件
jiangzesong@k8s-master:~/kubeadm_init$ cat kubeadm-init.yaml
apiVersion: kubeadm.k8s.io/v1beta3
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 10.156.112.98 # 修改自己的ip
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  name: k8s-master
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/k8s-master
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.aliyuncs.com/google_containers
kind: ClusterConfiguration
kubernetesVersion: v1.28.2
networking:
  dnsDomain: cluster.local
  podSubnet: 172.244.0.0/16 # pod的ip网段
  serviceSubnet: 192.96.0.0/12 # svc的pod网段
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
----------------------------------------------------------------------------------------------------
# 13.预拉取镜像
kubeadm config images pull --config kubeadm-init.yaml
----------------------------------------------------------------------------------------------------
# 14.初始化集群
kubeadm init --config=kubeadm-init.yaml
----------------------------------------------------------------------------------------------------
# 15. 配置 kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
----------------------------------------------------------------------------------------------------
# 16.配置网络插件
jiangzesong@k8s-master:~/kubeadm_init$ cat kube-flanne.yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    k8s-app: flannel
    pod-security.kubernetes.io/enforce: privileged
  name: kube-flannel
---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: flannel
  name: flannel
  namespace: kube-flannel
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: flannel
  name: flannel
rules:
- apiGroups:
  - ""
  resources:
  - pods
  verbs:
  - get
- apiGroups:
  - ""
  resources:
  - nodes
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - nodes/status
  verbs:
  - patch
- apiGroups:
  - networking.k8s.io
  resources:
  - clustercidrs
  verbs:
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: flannel
  name: flannel
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: flannel
subjects:
- kind: ServiceAccount
  name: flannel
  namespace: kube-flannel
---
apiVersion: v1
data:
  cni-conf.json: |
    {
      "name": "cbr0",
      "cniVersion": "0.3.1",
      "plugins": [
        {
          "type": "flannel",
          "delegate": {
            "hairpinMode": true,
            "isDefaultGateway": true
          }
        },
        {
          "type": "portmap",
          "capabilities": {
            "portMappings": true
          }
        }
      ]
    }
  net-conf.json: |
    {
      "Network": "172.244.0.0/16", # 改成pod的ip网段
      "Backend": {
        "Type": "vxlan"
      }
    }
kind: ConfigMap
metadata:
  labels:
    app: flannel
    k8s-app: flannel
    tier: node
  name: kube-flannel-cfg
  namespace: kube-flannel
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app: flannel
    k8s-app: flannel
    tier: node
  name: kube-flannel-ds
  namespace: kube-flannel
spec:
  selector:
    matchLabels:
      app: flannel
      k8s-app: flannel
  template:
    metadata:
      labels:
        app: flannel
        k8s-app: flannel
        tier: node
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                - linux
      containers:
      - args:
        - --ip-masq
        - --kube-subnet-mgr
        - --iface=enp2s0 # 改成自己的主机网卡 
        command:
        - /opt/bin/flanneld
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: EVENT_QUEUE_DEPTH
          value: "5000"
        image: registry.us-east-1.aliyuncs.com/oll/flannel:v0.25.4
        name: kube-flannel
        resources:
          requests:
            cpu: 100m
            memory: 50Mi
        securityContext:
          capabilities:
            add:
            - NET_ADMIN
            - NET_RAW
          privileged: false
        volumeMounts:
        - mountPath: /run/flannel
          name: run
        - mountPath: /etc/kube-flannel/
          name: flannel-cfg
        - mountPath: /run/xtables.lock
          name: xtables-lock
      hostNetwork: true
      initContainers:
      - args:
        - -f
        - /flannel
        - /opt/cni/bin/flannel
        command:
        - cp
        image: registry.us-east-1.aliyuncs.com/oll/flannel-cni-plugin:v1.4.1-flannel1
        name: install-cni-plugin
        volumeMounts:
        - mountPath: /opt/cni/bin
          name: cni-plugin
      - args:
        - -f
        - /etc/kube-flannel/cni-conf.json
        - /etc/cni/net.d/10-flannel.conflist
        command:
        - cp
        image: registry.us-east-1.aliyuncs.com/oll/flannel:v0.25.4
        name: install-cni
        volumeMounts:
        - mountPath: /etc/cni/net.d
          name: cni
        - mountPath: /etc/kube-flannel/
          name: flannel-cfg
      priorityClassName: system-node-critical
      serviceAccountName: flannel
      tolerations:
      - effect: NoSchedule
        operator: Exists
      volumes:
      - hostPath:
          path: /run/flannel
        name: run
      - hostPath:
          path: /opt/cni/bin
        name: cni-plugin
      - hostPath:
          path: /etc/cni/net.d
        name: cni
      - configMap:
          name: kube-flannel-cfg
        name: flannel-cfg
      - hostPath:
          path: /run/xtables.lock
          type: FileOrCreate
        name: xtables-lock
----------------------------------------------------------------------------------------------------        
# 17.去除污点
kubectl taint node k8s-master node-role.kubernetes.io/k8s-master-
kubectl taint node k8s-master node.kubernetes.io/not-ready:NoSchedule-
kubectl rollout restart deployment -n kube-system coredns
```

