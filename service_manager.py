import logging as log
import subprocess
from abc import ABC, abstractmethod
from contextlib import contextmanager, AbstractContextManager

_logger = log.getLogger("ServiceManager")


class AbstractServiceManager(ABC):

    @abstractmethod
    def run(self, name: str):
        ...

    @abstractmethod
    def stop(self, name: str):
        ...

    @abstractmethod
    @contextmanager
    def service_rerun(self, name: str) -> AbstractContextManager[None]:
        ...


class SystemdManager(AbstractServiceManager):

    def __init__(self):
        ...

    @classmethod
    def run(cls, name: str):
        _logger.info(f"Запуск сервиса {name}")
        subprocess.run(f"systemctl start {name}", check=True)

    @classmethod
    def stop(cls, name: str):
        _logger.info(f"Остановка сервиса {name}")
        subprocess.run(f"systemctl stop {name}", check=True)

    @classmethod
    @contextmanager
    def service_rerun(cls, name: str) -> AbstractContextManager[None]:
        cls.stop(name)
        try:
            yield
        finally:
            cls.run(name)


class WindowsServicesManager(AbstractServiceManager):
    ServiceStatus = tuple[int, int, int, int, int, int, int]

    def __init__(self):
        import win32serviceutil
        self.win32_api = win32serviceutil

    def _get_status(self, name: str) -> ServiceStatus:
        _logger.info(f"Получение статуса сервиса {name}")
        return self.win32_api.QueryServiceStatus(name)

    def run(self, name: str):
        status = self._get_status(name)
        if status[1] == 1:
            _logger.info(f"Запуск сервиса {name}")
            self.win32_api.StartService(name)

    def stop(self, name: str):
        status = self._get_status(name)
        if status[1] != 1:
            _logger.info(f"Остановка сервиса {name}")
            self.win32_api.StopService(name)

    @contextmanager
    def service_rerun(self, name: str) -> AbstractContextManager[None]:
        self.stop(name)
        try:
            yield
        finally:
            self.run(name)
