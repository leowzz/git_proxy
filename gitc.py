#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import subprocess
import sys

from loguru import logger

proxy_host = "127.0.0.1"
proxy_port = 13156

proxy_conf = {
    "http.proxy": f"http://{proxy_host}:{proxy_port}",
    "https.proxy": f"http://{proxy_host}:{proxy_port}"
}


def set_proxy():
    for k, v in proxy_conf.items():
        os.system(f"git config --global {k} {v}")


def clone(origin: str):
    clone_cmd = f"git clone {origin}"
    logger.info(f"cloning: from {origin}")
    res = subprocess.run(clone_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        logger.success(res.stderr)
    else:
        logger.error(f"err_code{res.returncode}: {res.stderr}")


def unset_proxy():
    for k, _ in proxy_conf.items():
        os.system(f"git config --global --unset {k}")
    logger.info(f"finish with unset proxy")


def main():
    logger.debug(f"{sys.argv=}")
    try:
        set_proxy()
        clone(sys.argv[1])
    except IndexError:
        logger.error(f"git origin url not found in: {sys.argv}")
    except KeyboardInterrupt:
        logger.info("用户终止操作")
    finally:
        unset_proxy()


if __name__ == '__main__':
    main()
