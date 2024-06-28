import tkinter as tk
from tkinter import messagebox
import mysql.connector

class LoginFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.label_title = tk.Label(self, text="Food Delivery Service", font=("Helvetica", 16, "bold"))
        self.label_welcome = tk.Label(self, text="Welcome to  Food Delivery Service", font=("Helvetica", 12))
        self.label_user_id = tk.Label(self, text="User ID:")
        self.entry_user_id = tk.Entry(self)
        self.label_pin = tk.Label(self, text="PIN:")
        self.entry_pin = tk.Entry(self, show="*")
        self.btn_login = tk.Button(self, text="Login", command=self.login)
        self.btn_register = tk.Button(self, text="Register", command=lambda: app.show_frame("RegisterFrame"))
        self.btn_quit = tk.Button(self, text="Quit", command=master.quit)

        self.label_title.pack(pady=10)
        self.label_welcome.pack(pady=5)
        self.label_user_id.place(x=50, y=100)
        self.entry_user_id.place(x=150, y=100)
        self.label_pin.place(x=50, y=130)
        self.entry_pin.place(x=150, y=130)
        self.btn_login.place(x=150, y=160)
        self.btn_register.place(x=210, y=160)
        self.btn_quit.place(x=150, y=190)

    def login(self):
        user_id = self.entry_user_id.get()
        pin = self.entry_pin.get()

        self.app.cursor.execute("SELECT pin FROM users WHERE user_id = %s", (user_id,))
        result = self.app.cursor.fetchone()

        if result and result[0] == pin:
            self.app.current_user_id = user_id
            self.app.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid User ID or PIN")

class HomePage(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.label_welcome = tk.Label(self, text="", font=("Helvetica", 14))
        self.label_welcome.pack(pady=10)

        self.btn_view_menu = tk.Button(self, text="View Menu", command=self.view_menu)
        self.btn_place_order = tk.Button(self, text="Place Order", command=lambda: app.show_frame("OrderFrame"))
        self.btn_view_orders = tk.Button(self, text="View Order History", command=self.view_orders)
        self.btn_logout = tk.Button(self, text="Logout", command=lambda: app.show_frame("LoginFrame"))

        self.btn_view_menu.pack(pady=5)
        self.btn_place_order.pack(pady=5)
        self.btn_view_orders.pack(pady=5)
        self.btn_logout.pack(pady=5)

    def update_welcome_message(self):
        self.label_welcome.config(text=f"Welcome, User {self.app.current_user_id}!")

    def view_menu(self):
        self.app.cursor.execute("SELECT dish_id, name, price FROM menu")
        menu_items = self.app.cursor.fetchall()

        menu_text = "\n".join([f"{dish[0]}: {dish[1]} - ${dish[2]}" for dish in menu_items])
        messagebox.showinfo("Menu", menu_text)

    def view_orders(self):
        self.app.cursor.execute("SELECT dish_id, quantity, total_price, order_date FROM orders WHERE user_id = %s", (self.app.current_user_id,))
        orders = self.app.cursor.fetchall()

        order_text = "\n".join([f"Dish ID: {order[0]}, Quantity: {order[1]}, Total Price: ${order[2]}, Date: {order[3]}" for order in orders])
        messagebox.showinfo("Order History", order_text)

class OrderFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        tk.Label(self, text="Enter Dish ID:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_dish_id = tk.Entry(self)
        self.entry_dish_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Enter Quantity:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_quantity = tk.Entry(self)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Enter PIN to confirm:").grid(row=2, column=0, padx=10, pady=5)
        self.entry_pin_confirm = tk.Entry(self, show="*")
        self.entry_pin_confirm.grid(row=2, column=1, padx=10, pady=5)

        self.btn_confirm = tk.Button(self, text="Confirm", command=self.confirm_order)
        self.btn_confirm.grid(row=3, columnspan=2, pady=10)

        self.btn_back = tk.Button(self, text="Back", command=lambda: app.show_frame("HomePage"))
        self.btn_back.grid(row=4, columnspan=2, pady=10)

    def confirm_order(self):
        dish_id = self.entry_dish_id.get()
        quantity = int(self.entry_quantity.get())
        pin = self.entry_pin_confirm.get()

        self.app.cursor.execute("SELECT pin FROM users WHERE user_id = %s", (self.app.current_user_id,))
        result = self.app.cursor.fetchone()

        if result and result[0] == pin:
            self.app.cursor.execute("SELECT price FROM menu WHERE dish_id = %s", (dish_id,))
            dish_price = self.app.cursor.fetchone()

            if dish_price:
                total_price = dish_price[0] * quantity
                self.app.cursor.execute("INSERT INTO orders (user_id, dish_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                                        (self.app.current_user_id, dish_id, quantity, total_price))
                self.app.db.commit()
                messagebox.showinfo("Success", f"Order placed successfully! Total price: ${total_price}")
            else:
                messagebox.showerror("Error", "Invalid Dish ID")
        else:
            messagebox.showerror("Error", "Invalid PIN")

class RegisterFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        tk.Label(self, text="User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_user_id = tk.Entry(self)
        self.entry_user_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="PIN:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_pin = tk.Entry(self, show="*")
        self.entry_pin.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self, text="Register", command=self.register_user).grid(row=2, columnspan=2, pady=10)
        tk.Button(self, text="Back", command=lambda: app.show_frame("LoginFrame")).grid(row=3, columnspan=2, pady=10)

    def register_user(self):
        user_id = self.entry_user_id.get()
        pin = self.entry_pin.get()

        try:
            self.app.cursor.execute("INSERT INTO users (user_id, pin) VALUES (%s, %s)", (user_id, pin))
            self.app.db.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            self.app.show_frame("LoginFrame")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

class FoodDeliveryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Food Delivery Service")
        self.master.geometry("400x300")

        # MySQL connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Avva@1234",
            database="food_delivery10_db"
        )
        self.cursor = self.db.cursor()

        self.current_user_id = None

        # Create frames
        self.frames = {}
        for F in (LoginFrame, HomePage, OrderFrame, RegisterFrame):
            page_name = F.__name__
            frame = F(master=self.master, app=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "HomePage":
            frame.update_welcome_message()
        frame.tkraise()

def main():
    root = tk.Tk()
    app = FoodDeliveryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
