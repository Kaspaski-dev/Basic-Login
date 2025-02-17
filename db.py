import sqlite3


def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'admin'))
    );
    ''')

    # Insertar usuarios por defecto (admin y usuario)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, role) VALUES 
    ('admin', 'admin123', 'admin'),
    ('user', 'user123', 'user');
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
