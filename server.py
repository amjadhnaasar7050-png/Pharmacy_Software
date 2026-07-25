from flask import Flask, render_template, jsonify, request, redirect
import mysql.connector
from datetime import datetime, timedelta
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Helper function to get a fresh DB connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQLPORT", 32202))
    )

@app.route("/")
def home():
    return render_template("phar_main.html")

@app.route("/phar_main.html")
def phar_main():
    return render_template("phar_main.html")

@app.route("/stock.html")
def stock():
    return render_template("stock.html")

@app.route("/SecondPage.html")
def SecondPage():
    return render_template("SecondPage.html")

@app.route("/suppliers.html")
def suppliers():
    return render_template("suppliers.html")

@app.route("/alerts.html")
def alerts():
    return render_template("alerts.html")

@app.route("/sell.html")
def sell():
    return render_template("sell.html")

@app.route("/sales.html")
def sales():
    return render_template("sales.html")

@app.route("/purchase.html")
def purchase():
    return render_template("purchase.html")

@app.route("/buy.html")
def buy():
    return render_template("buy.html")

# Products route
@app.route("/products")
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

# Sales route
@app.route("/sales")
def get_sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sales)

# Suppliers route
@app.route("/suppliers")
def get_suppliers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(suppliers)

# Purchase route
@app.route("/purchase")
def get_purchase():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM purchase")
    purchase = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(purchase)

# Add Product
@app.route("/add_product", methods=["POST"])
def add_product():
    conn = get_db_connection()
    cursor = conn.cursor()
    product_id = request.form["product_id"]
    price = request.form["price"]
    expiry_date = request.form["expiry_date"]
    name = request.form["name"]
    batch_no = request.form["batch_no"]
    supplier_id = request.form["sup_id"]
    stock = request.form["stock"]

    cursor.execute(
        "INSERT INTO products (product_id, price, expiry_date, name, batch_no, sup_id, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (product_id, price, expiry_date, name, batch_no, supplier_id, stock)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("stock.html")

# Add Purchase
@app.route("/add_buy", methods=["POST"])
def add_buy():
    conn = get_db_connection()
    cursor = conn.cursor()
    purchase_id = request.form["purchase"]
    name = request.form["name"]
    date = request.form["date"]
    amount_purchase = request.form["amount"]
    payment_p = request.form["method"]

    cursor.execute(
        "INSERT INTO purchase (purchase_id, name, date, amount_purchase, payment_p) VALUES (%s, %s, %s, %s, %s)",
        (purchase_id, name, date, amount_purchase, payment_p)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("buy.html")

# Delete Purchase
@app.route("/delete_purchase", methods=["POST"])
def delete_purchase():
    conn = get_db_connection()
    cursor = conn.cursor()
    purchase_id = request.form["purchase_id"]
    cursor.execute("DELETE FROM purchase WHERE purchase_id = %s", (purchase_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("buy.html")

# Delete Product
@app.route("/delete_product", methods=["POST"])
def delete_product():
    conn = get_db_connection()
    cursor = conn.cursor()
    product_id = request.form["product_id"]
    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("buy.html")

# Add Supplier
@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    conn = get_db_connection()
    cursor = conn.cursor()
    sup_id = request.form["sup_id"]
    name = request.form["name"]
    contact_no = request.form["contact_no"]
    origin = request.form["origin"]
    email = request.form["email"]

    cursor.execute(
        "INSERT INTO suppliers (sup_id, name, contact_no, origin, email) VALUES (%s, %s, %s, %s, %s)",
        (sup_id, name, contact_no, origin, email)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("suppliers.html")

# Delete Supplier
@app.route("/delete_supplier", methods=["POST"])
def delete_supplier():
    conn = get_db_connection()
    cursor = conn.cursor()
    sup_id = request.form["sup_id"]
    cursor.execute("DELETE FROM products WHERE sup_id = %s", (sup_id,))
    cursor.execute("DELETE FROM suppliers WHERE sup_id = %s", (sup_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("suppliers.html")

# Alerts
@app.route("/alerts/data")
def alerts_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, stock, expiry_date, sup_id FROM products")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    alerts = []
    for product_id, name, stock, expiry_date, sup_id in rows:
        if stock <= 20:
            alerts.append({"product_id": product_id, "name": name, "sup_id": sup_id, "message": "🔻 Low Stock"})
        if expiry_date <= (datetime.today().date() + timedelta(days=90)):
            alerts.append({"product_id": product_id, "name": name, "sup_id": sup_id, "message": "⚠️ Expiry Soon"})
    return jsonify(alerts)

@app.route("/sell_product", methods=["POST"])
def sell_product():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    product_id = (data.get("product_id"))
    qty = (data.get("qty"))
    name = data.get("name")
    amount = data.get("amount")
    payment = data.get("payment")

    cursor.execute(
        "INSERT INTO sales (name, date, amount_sales, payment_s) VALUES (%s, %s, %s, %s)",
        (name, datetime.now(), amount, payment)
    )
    cursor.execute("UPDATE products SET stock = stock - %s WHERE product_id = %s", (qty, product_id))
    cursor.execute("SELECT stock FROM products WHERE product_id = %s", (product_id,))

    updated_stock = cursor.fetchone()
   
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "product_id": product_id,
        "sold_qty": qty,
        "updated_stock": updated_stock[0] if updated_stock else None
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)
