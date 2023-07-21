# CB-deliveryboy - КБ-доставщик

Инструмент для обновления компонентов системы КБ

## Зависимости
1. Windows 10+
2. Python 3.10+

## Установка
1. `python3 -m pip install -r requirements.txt`

## Запуск
`python3 cb-delivery.py --config your_config.yaml`

### Доcтупные аргументы запуска
- `-c` `--config` - указать файл конфига (по-умолчанию `./config.yaml`)
- `-l` `--log-level` - установить уровень логов (`debug`, `info`, `warn`, `error`) 
- `-h` `--help` - вывод актуального списка всех доступных аргументов