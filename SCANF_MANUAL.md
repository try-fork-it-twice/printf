# Scanf Project Manual

## Overview
Scanf is a single-header library to track and save kernel events of FreeRTOS embedded system.

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Examples](#examples)

## Installation
```bash
pip install itmo-ics-printf
```

## Basic Usage
```python
from itmo_ics_printf import TraceLog

tracelog = TraceLog.load("my_stack_trace.bin")

tracelog.plot()
```

## Examples
### Get a diagram with everything
```python
from itmo_ics_printf import TraceLog

tracelog = TraceLog.load("my_stack_trace.bin")

tracelog.plot()
```

### Pick only events of first task
```python
from itmo_ics_printf import plot_events
from itmo_ics_printf.events import TaskCreate, TaskSwitchedIn, TaskSwitchedOut

# Select only events of task #1
events = [
    event
    for event in tracelog.events
    if isinstance(event, (TaskCreate, TaskSwitchedIn, TaskSwitchedOut)) and event.task_number == 1
]
plot_events(events)
```