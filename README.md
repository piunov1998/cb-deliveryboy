# CB-deliveryboy - КБ-доставщик

Инструмент для обновления компонентов системы КБ

## Зависимости
1. Windows 10+ или Linux
2. Python 3.11+
3. Poetry (для контроля зависимостей)

## Установка
1. `poetry install`

## Установка без Poetry
1. `python3 -m pip install pyyaml==6.0.1 pydantic==2.0.3`
2. Только для Windows `python3 -m pip install pywin32==306`

## Запуск
`python3 cb-delivery.py --config your_config.yaml`

### Доcтупные аргументы запуска
- `-c` `--config` - указать файл конфига (по-умолчанию `./config.yaml`)
- `-l` `--log-level` - установить уровень логов (`debug`, `info`, `warn`, `error`) 
- `-h` `--help` - вывод актуального списка всех доступных аргументов