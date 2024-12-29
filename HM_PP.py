import psycopg2

# Функция, создающая структуру БД (таблицы)
def create_tables(conn):
    cursor = conn.cursor()
    
    # Создание таблицы клиентов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
    """)
    
    # Создание таблицы телефонов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES Clients(id) ON DELETE CASCADE,
            phone VARCHAR(15) NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()

# Функция, позволяющая добавить нового клиента
def add_client(conn, first_name, last_name, email):
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Clients (first_name, last_name, email)
        VALUES (%s, %s, %s)
    """, (first_name, last_name, email))
    
    conn.commit()
    cursor.close()

# Функция для добавления телефона для существующего клиента
def add_phone(conn, client_id, phone):
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Phones (client_id, phone)
        VALUES (%s, %s)
    """, (client_id, phone))
    
    conn.commit()
    cursor.close()

# Функция, позволяющая изменить данные о клиенте
def update_client(conn, client_id, first_name=None, last_name=None, email=None):
    cursor = conn.cursor()
    
    if first_name:
        cursor.execute("""
            UPDATE Clients
            SET first_name = %s
            WHERE id = %s
        """, (first_name, client_id))
    
    if last_name:
        cursor.execute("""
            UPDATE Clients
            SET last_name = %s
            WHERE id = %s
        """, (last_name, client_id))
    
    if email:
        cursor.execute("""
            UPDATE Clients
            SET email = %s
            WHERE id = %s
        """, (email, client_id))
    
    conn.commit()
    cursor.close()

# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, phone_id):
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM Phones
        WHERE id = %s
    """, (phone_id,))
    
    conn.commit()
    cursor.close()

# Функция, позволяющая удалить существующего клиента
def delete_client(conn, client_id):
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM Clients
        WHERE id = %s
    """, (client_id,))
    
    conn.commit()
    cursor.close()
    print(f"Клиент с ID {client_id} удален.")

# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    try:
        cursor = conn.cursor()
        
        query = "SELECT c.id, c.first_name, c.last_name, c.email FROM Clients c"
        conditions = []
        params = []

        if first_name:
            conditions.append("c.first_name ILIKE %s")
            params.append(f"%{first_name}%")
        if last_name:
            conditions.append("c.last_name ILIKE %s")
            params.append(f"%{last_name}%")
        if email:
            conditions.append("c.email ILIKE %s")
            params.append(f"%{email}%")
        if phone:
            conditions.append("EXISTS (SELECT 1 FROM Phones p WHERE p.client_id = c.id AND p.phone ILIKE %s)")
            params.append(f"%{phone}%")
        
        if conditions:
            query += " WHERE " + " OR ".join(conditions)
        
        cursor.execute(query, params)
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            print(f"Искомый клиент: ID={result[0]}, Имя={result[1]}, Фамилия={result[2]}, Email={result[3]}")
        else:
            print("Клиент не найден.")
    
    except Exception as e:
        print(e)


def main():
    conn = psycopg2.connect(database='test_db', user='postgres', password='postgres')
    
    # Создание таблиц
    create_tables(conn)
    
    # Добавление клиентов
    add_client(conn, 'Lionel', 'Messi', 'fcb_lm9@gmail.com')
    add_client(conn, 'Cristiano', 'Ronaldo', 'rm_cr7.@gmail.com')
    
    # Добавление телефона клиента
    add_phone(conn, 1, '8-962-786-4052')
    
    # Изменение данных клиента
    update_client(conn, client_id=2, first_name='Vinicius', last_name='Junior')

    # Удаление телефона
    delete_phone(conn, 1)
    
    # Поиск клиента
    find_client(conn, first_name='Vinicius')

    # Удаление клиента
    delete_client(conn, 1)
    delete_client(conn, 2)

    conn.close()

if __name__ == "__main__":
    main()
