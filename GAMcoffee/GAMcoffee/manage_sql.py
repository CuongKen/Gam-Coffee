import sqlite3

def add_image_column(db_path="database.db"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE menus ADD COLUMN image TEXT")
    connection.commit()
    connection.close()
    print("Added 'image' column to 'menus' table.")

if __name__ == "__main__":
    add_image_column()