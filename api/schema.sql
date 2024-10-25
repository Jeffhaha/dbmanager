CREATE TABLE IF NOT EXISTS databases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    host TEXT NOT NULL,
    port TEXT NOT NULL,
    user TEXT NOT NULL,
    password TEXT NOT NULL,
    database TEXT NOT NULL,
    status TEXT NOT NULL
);
