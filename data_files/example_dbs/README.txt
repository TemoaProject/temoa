The exemplar databases here are version controlled in textual .sql format, which is more workable
with Git than binary .sqlite files.

If you wish to use them, use sqlite to convert them to database format.  The command is:

> sqlite3 utopia.sqlite < utopia.sql

This command will make the sqlite database from the sql commands
