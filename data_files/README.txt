This directory contains sample files that can be used to test Temoa.

Temoa works by reading a relational database (sqlite).

*.sql files represent text files of SQL commands used to construct a relational database file.

*.sqlite files represent the compiled sqlite databases. A sqlite file
is created from a sql file using sqlite, which is freely available:
https://sqlite.org/index.html. From the command prompt:

$ sqlite3 temoa_utopia.sqlite < temoa_utopia.sql
