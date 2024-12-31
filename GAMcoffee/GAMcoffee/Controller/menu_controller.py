import os
from flask import request, redirect, url_for, current_app, render_template
from Model.menu_model import MenuModel

class MenuController:
    def __init__(self):
        self.model = MenuModel()

    def request_menu(self):
        menu_items = self.model.get_menu()
        return render_template("menu.html", items=menu_items)

    def create_menu(self):
        return render_template("menu_form.html")

    def store_menu(self):
        # Retrieve form data
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")

        # Convert price to float
        if price:
            price = float(price)

        # Handle file upload
        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename != "":
            # Validate file extension
            allowed_extensions = {"jpg", "jpeg", "png", "gif"}
            ext = image_file.filename.rsplit(".", 1)[-1].lower()
            if ext in allowed_extensions:
                # Create a secure filename, store in static folder
                image_filename = image_file.filename
                upload_path = os.path.join(
                    current_app.root_path, "static", "uploads", image_filename
                )
                image_file.save(upload_path)

        # Call model to store in DB
        self.model.store_menu(name, price, description, image_filename)

        # Redirect to the menu page
        return redirect(url_for("show_menu_list"))

    def list_menu(self):
        menu = self.model.get_menu()
        return render_template("list_menu.html", items=menu)

    def edit_menu(self, item_id):
        menu_item = self.model.get_menu_item_by_id(item_id)
        if menu_item:
            if request.method == 'POST':
                name = request.form['name']
                price = float(request.form['price'])
                description = request.form['description']

                return self.update_menu(item_id, name, price, description)

            return render_template('edit_menu.html', item=menu_item)
        return "Item not found", 404

    def update_menu(self, item_id, name, price, description):
        if self.model.update_menu_item(item_id, name, price, description):
            return redirect(url_for('show_menu_list'))
        else:
            return "Error updating menu item", 500

    def delete_menu(self, item_id):
        self.model.delete_menu(item_id)
        return redirect(url_for("show_menu"))

    def buy_now(self, item_id):
        if request.method == 'POST':
            name = request.form.get("name")
            quantity = int(request.form.get("quantity"))
            price = float(request.form.get("price"))

            total_price = quantity * price

            self.model.store_order(name, quantity, price, total_price)

            return render_template("order_confirmation.html", name=name, quantity=quantity, total_price=total_price)
        else:
            menu_item = self.model.get_menu_item_by_id(item_id)
            return render_template("buy_now.html", item=menu_item)