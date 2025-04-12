## Supported Events

> Search for `#define trace<event name>` in the FreeRTOS-Kernel codebase to find event documentation and details about available arguments.

### 0.x.x

These events must be implemented as part of the initial MVP version of `scanf/printf`. This involves support for basic task events.

#### 1. TASK_CREATE

**When:** Triggered when a task is created using `xTaskCreate()` or `xTaskCreateStatic()`.

**Details:** This event occurs immediately after the task's memory is allocated (if dynamic allocation is used) and its Task Control Block (TCB) is initialized, but before the task is added to the scheduler's ready list.

**Trace macro:** `traceTASK_CREATE( pxNewTCB )`

**Parameters:** A new task control block (see `struct tskTaskControlBlock` in `task.c`) is passed as a trace macro parameter.

#### 2. TASK_SWITCHED_IN

**When:** Triggered when a task is switched in by the scheduler and starts executing.

**Details:** This happens during a context switch when the scheduler selects the task to run (e.g., after creation, resuming from suspension, or when a higher-priority task becomes ready).

**Trace macro:** `traceTASK_SWITCHED_IN()`

**Parameters:** A pointer to the task control block is available within the macro's scope as the `pxCurrentTCB` variable.

#### 3. TASK_SWITCHED_OUT

**When:** Triggered when a task is switched out by the scheduler and stops executing.

**Details:** This occurs when the scheduler preempts the task (e.g., due to a higher-priority task becoming ready, the task yielding, or blocking on a delay/semaphore/queue).

**Trace macro:** `traceTASK_SWITCHED_OUT()`

**Parameters:** A pointer to the task control block is available within the macro's scope as the `pxCurrentTCB` variable.

### 1.x.x

This milestone completes basic task event tracking by handling different task states such as delayed, suspended, and blocked (e.g., on a queue, semaphore, or mutex).

### 2.x.x

This milestone introduces support for tracking I/O and ISR events.

## Trace Log Format

The trace log is an array consisting of trace messages. Each trace message contains `event_type` and `timestamp` as its first members. The specific event message structure is determined by `event_type`.

```c
#define SCANF_MAX_TASK_NAME_LEN 64

typedef enum : uint8_t {
    TASK_CREATE,
    TASK_SWITCHED_IN,
    TASK_SWITCHED_OUT
} SCANF_EventType;

typedef struct __attribute__((__packed__)) {
    uint8_t event_type; /**< One of the SCANF_EventType values specifying the event type. Full event details must be retrieved from the corresponding structure. */
    uint32_t timestamp;  /**< Timestamp when the event occurred, in microseconds since system start. */
} SCANF_TraceMessage;

typedef struct __attribute__((__packed__)) {
    uint8_t event_type; /**< Must be SCANF_EventType.TASK_CREATE */
    uint32_t timestamp;
    uint32_t task_number; /**< Unique identifier of the newly created task. */
    char task_name[SCANF_MAX_TASK_NAME_LEN]; /**< Null-terminated task name. May be truncated if `configMAX_TASK_NAME_LEN` exceeds `SCANF_MAX_TASK_NAME_LEN`. */
} SCANF_TASK_CREATE_TraceMessage;

typedef struct __attribute__((__packed__)) {
    uint8_t event_type; /**< Must be SCANF_EventType.TASK_SWITCHED_IN */
    uint32_t timestamp;
    uint32_t task_number;
} SCANF_TASK_SWITCHED_IN_TraceMessage;

typedef struct __attribute__((__packed__)) {
    uint8_t event_type; /**< Must be SCANF_EventType.TASK_SWITCHED_OUT */
    uint32_t timestamp;
    uint32_t task_number;
} SCANF_TASK_SWITCHED_OUT_TraceMessage;
```

## C API

```c
typedef void (*trace_log_overflow_handler_t)(SCANF_TraceLog*);

typedef struct {
    trace_log_overflow_handler_t overflow_handler; /**< Function pointer to be called when the message array exceeds its capacity. */
    uint32_t size; /**< Total size of the recorded trace log in bytes. */
    uint32_t capacity; /**< Allocated memory size (in bytes) for storing trace log messages. */
    SCANF_EventType messages[]; /**< Traced event messages. WARNING: Do not iterate using `sizeof(SCANF_EventType)`. Use the actual event message structure size, derived from `event_type`, to calculate the offset of the next entry. */
} SCANF_TraceLog;

/// Initialize the global trace log pointer with a user-allocated trace log structure.
void SCANF_INIT(SCANF_TraceLog* tracelog);

/// Retrieve the global trace log handler so the user can access its underlying data.
SCANF_TraceLog* SCANF_TRACELOG_HANDLER();

/// Reset the trace log size.
void SCANF_RESET();

/// Start recording events in the trace log.
void SCANF_START_TRACING();

/// Stop recording events in the trace log.
void SCANF_STOP_TRACING();
```
