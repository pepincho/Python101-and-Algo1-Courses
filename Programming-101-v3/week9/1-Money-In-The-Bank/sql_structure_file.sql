DROP TABLE IF EXISTS Clients;

CREATE TABLE IF NOT EXISTS Clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    balance REAL DEFAULT 0,
    message TEXT);
