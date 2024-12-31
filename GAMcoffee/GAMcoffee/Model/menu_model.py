import sqlite3

class MenuModel:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    def store_menu(self, name, price, description, image_filename=None):
        """
        Insert a new menu item into the 'menu' table.
        `image_filename` is the name of the uploaded file (or None if not provided).
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO menu (name, price, description, image)
            VALUES (?, ?, ?, ?)
        """, (name, price, description, image_filename))

        connection.commit()
        connection.close()

    def get_menu_items(self):
        """
        Fetch all menu items from the 'menu' table.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, price, description, image FROM menu")
        results = cursor.fetchall()

        connection.close()

        menu_items = [
            {
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "description": row[3],
                "image": row[4],
            }
            for row in results
        ]

        return menu_items

    def get_menu_item_by_id(self, item_id):
        """
        Fetch a single menu item by its ID.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, price, description, image FROM menu WHERE id = ?", (item_id,))
        result = cursor.fetchone()

        connection.close()

        if result:
            return {
                "id": result[0],
                "name": result[1],
                "price": result[2],
                "description": result[3],
                "image": result[4],
            }
        return None

    def update_menu(self, item_id, name, price, description, image_filename=None):
        """
        Update a menu item in the 'menu' table.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE menu
            SET name = ?, price = ?, description = ?, image = ?
            WHERE id = ?
        """, (name, price, description, image_filename, item_id))

        connection.commit()
        connection.close()

    def delete_menu(self, item_id):
        """
        Delete a menu item from the 'menu' table.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))

        connection.commit()
        connection.close()