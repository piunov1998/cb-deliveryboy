import logging as log
import shutil
import time
from contextlib import contextmanager
from pathlib import Path

import win32serviceutil
from pydantic import BaseModel

SERVICE_STATUS = tuple[int, int, int, int, int, int, int]


class TrackingFile(BaseModel):
    name: str
    source: Path
    dest: Path

    def absolute(self) -> 'TrackingFile':
        return self.__class__(
            name=self.name,
            source=self.source.absolute(),
            dest=self.dest.absolute()
        )


@contextmanager
def service_rerun(name: str):
    log.info(f"Получение статуса сервиса {name}")
    status: SERVICE_STATUS = win32serviceutil.QueryServiceStatus(name)

    if status[1] != 1:
        log.info(f"Остановка сервиса {name}")
        win32serviceutil.StopService(name)

    try:
        yield
    finally:
        status: SERVICE_STATUS = win32serviceutil.QueryServiceStatus(name)
        if status[1] == 1:
            log.info(f"Запуск сервиса {name}")
            win32serviceutil.StartService(name)


class Worker:

    def __init__(self, tracking_files: list[TrackingFile], interval: float = 1.0):
        self.tracking_files = [file.absolute() for file in tracking_files]
        self.interval = interval

    @staticmethod
    def proceed(file: TrackingFile):
        if not file.source.is_file():
            raise Exception(f"{file.source} не является файлом")
        log.info(f"Файл обнаружен -> {file.name}")

        with service_rerun("ASM"):
            log.info("Замена исполняемого файла")
            shutil.move(file.source, file.dest)

        log.info(f"Готово")

    def __run(self) -> bool:
        success = False
        for file in self.tracking_files:
            log.debug(f"Проверка файла {file.source}")
            if file.source.exists():
                try:
                    self.proceed(file)
                    success = True
                except Exception as e:
                    log.error(f"Ошибка во время обработки файла -> {e}")
                    success = False
        return success

    def run(self):
        if len(self.tracking_files) == 0:
            raise Exception("Не указаны файлы для отслеживания")

        log.info(f"Ожидание файлов: {', '.join([str(file.name) for file in self.tracking_files])}")
        while True:
            if self.__run():
                time.sleep(self.interval)
                log.info(f"Ожидание файлов: {', '.join([str(file.name) for file in self.tracking_files])}")
            else:
                time.sleep(self.interval * 5)
