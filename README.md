# Git使用本地代理来克隆项目

## 配置

1. 克隆本项目
2. 为项目 `/bin` 配置环境变量
3. 修改 `/bin/gitc.bat` 将其中的路径配置成 gitc.py 的绝对路径
4. 安装依赖
   ```shell
   pip install loguru
   ```

## 使用

在你的工作目录执行

   ```shell
   gitc https://github.com/3181538941/git_proxy.git
   ```

执行效果
![img.png](img/img.png)

## 原理

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

