# Git使用本地代理来克隆项目

## 1. 配置

1. 克隆本项目
2. 为项目 `bin` 配置环境变量
3. 修改 `bin/gitc.bat` 将其中的路径配置成 gitc.py 的绝对路径
4. 修改 `gitc.py` 中的 `proxy_host`, `proxy_port` 改为你的代理配置
5. 安装依赖
   ```shell
   pip install loguru
   ```

## 2. 使用

在你的工作目录执行

   ```shell
   gitc https://github.com/3181538941/git_proxy.git
   ```

执行效果
![img.png](img/img.png)

## 3. fuck

代码推送过程中遇到了比较常见的问题
> fatal: unable to access 'https://github.com/3181538941/git_proxy.git/': OpenSSL SSL_read: Connection was reset, errno 10054

这种情况下就需要设置代理, 我意识到 需要脚本来实现设置代理和取消设置代理

所以添加了两个脚本 `bin/gsp.git`, `bin/gup.git`

分别对应 `git set proxy` 和 `git unset proxy` 的缩写

那这样的话 `gitc.py` 脚本也就相当于
> gsp
>
> git clone ...
>
> gup

## 4. 原理

1. 执行代理设置命令

    ```shell
    git config --global http.proxy http://127.0.0.1:7890
    git config --global https.proxy http://127.0.0.1:7890
    ```

2. 执行克隆命令

    ```shell
    git clone https://github.com/3181538941/git_proxy.git
    ```

3. 取消设置代理 避免影响git正常使用

    ```shell
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    ```

