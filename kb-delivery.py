import argparse
import ctypes
import logging
import platform
import re
import sys
import traceback
from pathlib import Path

import yaml

from config import Config
from worker import Worker

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR
}


def load_config(path: str | Path) -> Config:
    with open(path, 'r', encoding='utf-8') as stream:
        data = yaml.safe_load(stream)
    return Config.model_validate(data)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.warning(f"Не удалось получить информацию о правах администратора -> {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c --config', default='./config.yaml', metavar='config path', dest='config')
    parser.add_argument('-l --log-level', default='info', dest='log_level', choices=LOG_LEVELS.keys())
    namespace = parser.parse_args()

    fmt = f"[%(asctime)s] %(levelname)s | %(message)s"
    logging.basicConfig(level=LOG_LEVELS[namespace.log_level], stream=sys.stdout, format=fmt)

    if not re.fullmatch("Windows-?.+", platform.platform(True, True), flags=re.IGNORECASE):
        logging.fatal("Поддерживаются только Windows системы")
        sys.exit(0)

    if not is_admin():
        logging.warning("Перезапуск с правами администратора")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

    try:
        config = load_config(namespace.config)
    except Exception as e:
        logging.fatal(f"Ошибка при чтении конфига -> {e}")
        traceback.print_exception(e)
        input("Нажмите Enter для выхода")
        sys.exit(1)

    worker = Worker(config.tracking_files)

    try:
        worker.run()
    except Exception as e:
        logging.fatal(f"Непредвиденная ошибка -> {e}")
        traceback.print_exception(e)
        input("Нажмите Enter для выхода")
        sys.exit(1)


if __name__ == '__main__':
    main()
