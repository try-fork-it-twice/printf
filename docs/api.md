Data packet:
```
| timestamp | task_id | type |
|-----------|---------|------|
| u64       | u64     | u16  |
```

Data flow:

`[ [18 byte], [18 byte], ..., [18 byte] ]`

```
+-------+-------+-------+
| time  | task  | type  |
| stamp | id    |       |
+-------+-------+-------+
| time  | task  | type  |
| stamp | id    |       |
+-------+-------+-------+
...
+-------+-------+-------+
| time  | task  | type  |
| stamp | id    |       |
+-------+-------+-------+
```
