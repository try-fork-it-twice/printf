# Руководство по Printf Project

## Обзор
Printf - это программа для визуализации событий ядра встраиваемой системы FreeRTOS.

## Содержание
- [Установка](#installation)
- [Основы использования](#basic-usage)
- [Примеры](#examples)

## Установка
```bash
pip install itmo-ics-printf
```

## Основы использования
```python
from itmo_ics_printf import TraceLog

tracelog = TraceLog.load("my_stack_trace.bin")

tracelog.plot()
```

## Примеры
### Получение диаграммы со всеми событиями
```python
from itmo_ics_printf import TraceLog

tracelog = TraceLog.load("my_stack_trace.bin")

tracelog.plot()
```

### Выбор только событий первой задачи
```python
from itmo_ics_printf import plot_events
from itmo_ics_printf.events import TaskCreate, TaskSwitchedIn, TaskSwitchedOut

# Выбираем только события задачи №1
events = [
    event
    for event in tracelog.events
    if isinstance(event, (TaskCreate, TaskSwitchedIn, TaskSwitchedOut)) and event.task_number == 1
]
plot_events(events)
```
