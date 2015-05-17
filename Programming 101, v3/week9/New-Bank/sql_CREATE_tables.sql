CREATE TABLE IF NOT EXISTS Clients(
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_username TEXT,
    client_password TEXT,
    client_balance REAL DEFAULT 0,
    client_message TEXT,
    client_email TEXT);