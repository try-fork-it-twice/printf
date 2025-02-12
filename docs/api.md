Data packet:

| timestamp | task_id | type |

+-------+-------+-------+
| u64   | u64   | u64   |
|       |       |       |
+-------+-------+-------+

Data flow:

[ [24 byte], [24 byte], ..., [24 byte] ]

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