import logging as log
import shutil
import time
from pathlib import Path

from pydantic import BaseModel

from service_manager import AbstractServiceManager


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


class Worker:

    def __init__(
        self,
        service_manager: AbstractServiceManager,
        tracking_files: list[TrackingFile],
        interval: float = 1.0,
    ):
        self.service_manager = service_manager
        self.tracking_files = [file.absolute() for file in tracking_files]
        self.interval = interval

    def proceed(self, file: TrackingFile):
        if not file.source.is_file():
            raise Exception(f"{file.source} не является файлом")
        log.info(f"Файл обнаружен -> {file.name}")

        with self.service_manager.service_rerun("ASM"):
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
