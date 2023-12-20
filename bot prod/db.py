import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        
    def user_exists(self, id):
        with self.connection:
            result = self.cursor.execute("select * from users where id =?", (id,)).fetchall()
            return bool(len(result))
            
    def add_user(self, id):
        with self.connection:
            return self.connection.execute("INSERT INTO users (id) VALUES (?)", (id,))
        
    def get_balance(self, id):
        with self.connection:
            balance = self.connection.execute("SELECT balance FROM users WHERE id =?", (id,)).fetchone()[0]
            return balance
    
    def tow_name(self):
        with self.connection:
            tow = self.connection.execute("SELECT name FROM items")
            return tow.fetchall()
    def tow_desc(self):
        with self.connection:
            tow = self.connection.execute("SELECT desc FROM items")
            return tow.fetchall()
    def tow_price(self,id):
        with self.connection:
            tow = self.connection.execute("SELECT price FROM items WHERE id = ?",(id,))
            return tow.fetchone()
        
    def history_add(self,user_id, item_id, date):
        with self.connection:
            histi = self.connection.execute("INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)", (user_id, item_id, date,))
            return histi
    def my_history(self,user_id):
        with self.connection:
            hist = self.connection.execute("SELECT name,date FROM items JOIN bills ON items.id = bills.item_id WHERE user_id =?", (user_id,))
            return hist.fetchall()
        
    def add_balance(self, id, amount):
        with self.connection:
            return self.connection.execute("UPDATE users SET balance = balance +? WHERE id =?", (amount,id,))
    def remove_balance(self, id, amount):
        with self.connection:
            return self.connection.execute("UPDATE users SET balance = balance -? WHERE id =?", (amount, id,))
        
    def categories(self):
        with self.connection:
            return self.connection.execute("SELECT * FROM categories").fetchall()
        
    def categories_spis(self,category_id):
        with self.connection:
            return self.connection.execute("SELECT items.id, items.name FROM items INNER JOIN categories ON items.category_id = categories.id WHERE categories.id = ?",(category_id,)).fetchall()
    def items(self,items_id):
        with self.connection:
            return self.connection.execute("SELECT name, price FROM items WHERE id = ?",(items_id,)).fetchone()
        