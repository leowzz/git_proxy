#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import subprocess
import sys
from argparse import Namespace

from loguru import logger

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
default_conf = f"""[proxy]
host = 127.0.0.1
port = 7890
"""


class GitCloneProxy:
    """
    git clone proxy
    """

    def __init__(self, args: Namespace, _host: str = "127.0.0.1", _port: int = 13156):
        self.args = args
        self.proxy_conf = {
            "http.proxy": f"http://{_host}:{_port}",
            "https.proxy": f"http://{_host}:{_port}"
        }

    def set_proxy(self):
        for k, v in self.proxy_conf.items():
            os.system(f"git config --global {k} {v}")
        logger.info(f"finish with set proxy")

    def unset_proxy(self):
        for k, _ in self.proxy_conf.items():
            os.system(f"git config --global --unset {k}")
        logger.info(f"finish with unset proxy")

    def clone(self):
        clone_cmd = f"git clone {self.args.origin} " + " ".join(self.args.git_args)
        logger.info(f"<{clone_cmd=}>")
        # 输出到终端
        res = subprocess.run(clone_cmd, stdout=sys.stdout, stderr=sys.stderr, text=True, shell=True)
        if res.returncode == 0:
            logger.success(res.stderr)
        else:
            logger.error(f"err_code{res.returncode}: {res.stderr}")

    def __enter__(self):
        self.set_proxy()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"{exc_type=}, {exc_val=}, {exc_tb=}")
        self.unset_proxy()


# 初始化一个命令行程序
def init_cli():
    import argparse
    parser = argparse.ArgumentParser(description="gitc")
    # 非必选参数
    parser.add_argument("origin", help="git origin url", nargs="?", default="")

    # 自定义参数
    parser.add_argument("-s", "--set-proxy", action="store_true", help="set proxy")
    parser.add_argument("-u", "--unset-proxy", action="store_true", help="unset proxy")
    parser.add_argument("-d", "--debug", action="store_true", help="debug mode")
    parser.add_argument("-V", "--version", action="version", version="1.0.0")

    # 放行git clone 的参数
    parser.add_argument('git_args', nargs=argparse.REMAINDER, help="git clone 原始参数")

    args = parser.parse_args()
    return args


git_args_ = """
fatal: You must specify a repository to clone.

usage: git clone [<options>] [--] <repo> [<dir>]

    -v, --verbose         be more verbose
    -q, --quiet           be more quiet
    --progress            force progress reporting
    --reject-shallow      don't clone shallow repository
    -n, --no-checkout     don't create a checkout
    --bare                create a bare repository
    --mirror              create a mirror repository (implies bare)
    -l, --local           to clone from a local repository
    --no-hardlinks        don't use local hardlinks, always copy
    -s, --shared          setup as shared repository
    --recurse-submodules[=<pathspec>]
                          initialize submodules in the clone
    --recursive ...       alias of --recurse-submodules
    -j, --jobs <n>        number of submodules cloned in parallel
    --template <template-directory>
                          directory from which templates will be used
    --reference <repo>    reference repository
    --reference-if-able <repo>
                          reference repository
    --dissociate          use --reference only while cloning
    -o, --origin <name>   use <name> instead of 'origin' to track upstream
    -b, --branch <branch>
                          checkout <branch> instead of the remote's HEAD
    -u, --upload-pack <path>
                          path to git-upload-pack on the remote
    --depth <depth>       create a shallow clone of that depth
    --shallow-since <time>
                          create a shallow clone since a specific time
    --shallow-exclude <revision>
                          deepen history of shallow clone, excluding rev
    --single-branch       clone only one branch, HEAD or --branch
    --no-tags             don't clone any tags, and make later fetches not to follow them
    --shallow-submodules  any cloned submodules will be shallow
    --separate-git-dir <gitdir>
                          separate git dir from working tree
    -c, --config <key=value>
                          set config inside the new repository
    --server-option <server-specific>
                          option to transmit
    -4, --ipv4            use IPv4 addresses only
    -6, --ipv6            use IPv6 addresses only
    --filter <args>       object filtering
    --also-filter-submodules
                          apply partial clone filters to submodules
    --remote-submodules   any cloned submodules will use their remote-tracking branch
    --sparse              initialize sparse-checkout file to include only files at root
"""


def init_conf():
    # 在用户的主目录下创建 .gitc 目录
    home_dir = os.path.expanduser("~")
    conf_dir = os.path.join(home_dir, ".gitc")
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)
    # 在 .gitc 目录中创建 gitc.conf 文件
    conf_file = os.path.join(conf_dir, "gitc.conf")
    logger.debug(conf_file)
    if not os.path.exists(conf_file):
        with open(conf_file, "w") as f:
            f.write(default_conf)
        logger.debug(f"检测到配置文件不存在, 创建之🦨 -> {conf_file}")

    # 读取配置文件
    import configparser
    config = configparser.ConfigParser()
    config.read(conf_file)
    _host = config.get("proxy", "host")
    _port = config.getint("proxy", "port")
    logger.debug(f"从{conf_file}配置文件读取到 -> {_host=}, {_port=}")
    return _host, _port


def main_cli():
    args = init_cli()
    if not args.debug:
        # 将日志等级设置为INFO
        logger.remove()
        logger.add(sys.stdout, level="INFO")
    host, port = init_conf()
    logger.debug(f"{args=}")
    if args.set_proxy:
        GitCloneProxy(args, host, port).set_proxy()
        return
    elif args.unset_proxy:
        GitCloneProxy(args, host, port).unset_proxy()
        return
    elif not args.origin:
        logger.error("克隆地址不能为空")
        # 按任意键退出
        os.system("pause")
        return
    with GitCloneProxy(args, host, port) as proxy:
        proxy.clone()


if __name__ == '__main__':
    main_cli()
