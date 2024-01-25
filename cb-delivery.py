import argparse
import logging
import platform
import sys
import traceback
from enum import StrEnum
from pathlib import Path

import yaml

from config import Config
from worker import Worker

from service_manager import SystemdManager, WindowsServicesManager

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR
}


class SupportedOS(StrEnum):
    WINDOWS = "windows"
    LINUX = "linux"


def load_config(path: str | Path) -> Config:
    with open(path, 'r', encoding='utf-8') as stream:
        data = yaml.safe_load(stream)
    return Config.model_validate(data)


def is_admin():
    try:
        import ctypes
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

    os_name = platform.system().lower()

    if os_name == SupportedOS.WINDOWS and not is_admin():
        import ctypes
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

    match os_name:
        case SupportedOS.LINUX:
            service_manager = SystemdManager()
        case SupportedOS.WINDOWS:
            service_manager = WindowsServicesManager()
        case _:
            logging.fatal(f"Система не поддерживается. Поддерживаемые системы: [{', '.join(SupportedOS)}]")
            input("Нажмите Enter для выхода")
            sys.exit(1)

    worker = Worker(service_manager, config.tracking_files)

    try:
        worker.run()
    except Exception as e:
        logging.fatal(f"Непредвиденная ошибка -> {e}")
        traceback.print_exception(e)
        input("Нажмите Enter для выхода")
        sys.exit(1)


if __name__ == '__main__':
    main()
