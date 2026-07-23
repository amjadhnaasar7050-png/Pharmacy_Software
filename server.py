from flask import Flask,render_template, jsonify , request , redirect
import mysql.connector
from datetime import datetime,timedelta
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import os

db = mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQL_ROOT_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    port=int(os.getenv("MYSQLPORT", 32202))
)


cursor = db.cursor()

cursor.execute("SET GLOBAL wait_timeout = 28800")
cursor.execute("SET GLOBAL interactive_timeout = 28800")
cursor.execute("SET GLOBAL net_read_timeout = 1200")
cursor.execute("SET GLOBAL net_write_timeout = 1200")

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

#this is the route for getting products from database

@app.route("/products") 
def get_products():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return jsonify(products)

@app.route("/sales")
def get_sales():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    return jsonify(sales)

# Add Product
@app.route("/add_product", methods=["POST"])
def add_product():
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
    db.commit()
    return redirect("stock.html")  # redirect back to stock page

@app.route("/add_buy", methods=["POST"])
def add_buy():
    purchase_id = request.form["purchase"]
    name = request.form["name"]
    date = request.form["date"]
    amount_purchase = request.form["amount"]
    payment_p = request.form["method"]


    cursor.execute(
        "INSERT INTO purchase (purchase_id, name, date, amount_purchase, payment_p) VALUES (%s, %s, %s, %s, %s)",
        (purchase_id, name, date, amount_purchase, payment_p)
    )
    db.commit()
    return redirect("buy.html")  # redirect back to buy page


#delete product
@app.route("/delete_purchase", methods=["POST"])
def delete_purchase():
    purchase_id = request.form["purchase_id"]

    cursor.execute("DELETE FROM purchase WHERE purchase_id = %s", (purchase_id,))
    db.commit()
    return redirect("buy.html")

@app.route("/delete_product", methods=["POST"])
def delete_product():
    product_id = request.form["product_id"]

    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    db.commit()
    return redirect("buy.html")




@app.route("/suppliers") #this is the route for getting suppliers from database
def get_suppliers():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    return jsonify(suppliers)

@app.route("/purchase") #this is the route for getting purchase data from database
def get_purchase():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM purchase")
    purchase = cursor.fetchall()
    return jsonify(purchase)

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return {}, 200


@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    sup_id = request.form["sup_id"]
    name = request.form["name"]
    contact_no = request.form["contact_no"]
    origin = request.form["origin"]
    email = request.form["email"]

    cursor.execute(
        "INSERT INTO suppliers (sup_id, name, contact_no, origin, email) VALUES (%s, %s, %s, %s, %s)",
        (sup_id,name,contact_no,origin,email)
    )
    db.commit()
    return redirect("suppliers.html")  # redirect back to supplier page




@app.route("/delete_supplier", methods=["POST"])
def delete_supplier():
    sup_id = request.form["sup_id"]

    cursor.execute("DELETE FROM products WHERE sup_id = %s", (sup_id,))
    cursor.execute("DELETE FROM suppliers WHERE sup_id = %s", (sup_id,))
    db.commit()
    return redirect("suppliers.html")



#alerts

@app.route("/alerts/data")
def alerts_data():
    cursor.execute("SELECT product_id, name, stock, expiry_date,sup_id FROM products")
    rows = cursor.fetchall()

    alerts = []
    for product_id, name, stock, expiry_date,sup_id in rows:
        # Low stock condition
        if stock <= 20:
            alerts.append({
                "product_id": product_id,
                "name": name,
                "sup_id": sup_id,
                "message": "🔻 Low Stock"
            })
        # Expiry soon condition
        expiry = expiry_date
        if expiry <= (datetime.today().date() + timedelta(days=90)):
            alerts.append({
                "product_id": product_id,
                "name": name,
                "sup_id": sup_id,
                "message": "⚠️ Expiry Soon"
            })

    # Return JSON list of alerts
    return jsonify(alerts)



@app.route("/alertsc")
def alertsc():
    alert_type = request.args.get("type")  # "low", "expiry", or "all"

    cursor.execute("SELECT product_id, name, stock, expiry_date,sup_id FROM products")
    rows = cursor.fetchall()

    alertsc = []
    for product_id, name, stock, expiry_date, sup_id in rows:
        expiry = expiry_date

        if alert_type == "low" and stock < 20:
            alertsc.append({"product_id": product_id, "name": name, "message": "🔻 Low Stock", "sup_id": sup_id})
        elif alert_type == "expiry" and expiry <= (datetime.today().date() + timedelta(days=90)):
            alertsc.append({"product_id": product_id, "name": name, "message": "⚠️ Expiry Soon", "sup_id": sup_id})
        elif alert_type == "all":
            if stock < 20:
                alertsc.append({"product_id": product_id, "name": name, "message": "🔻 Low Stock", "sup_id": sup_id})
            if expiry <= (datetime.today().date() + timedelta(days=90)):
                alertsc.append({"product_id": product_id, "name": name, "message": "⚠️ Expiry Soon", "sup_id": sup_id})

    return jsonify(alertsc)



@app.route("/sell_product", methods=["POST"])
def sell_product():
    data = request.get_json()
    product_id = int(data.get("product_id"))   # must be integer
    qty = int(data.get("qty"))
    name = data.get("name")
    amount = data.get("amount")
    payment = data.get("payment")

    cursor.execute("""
        INSERT INTO sales (name, date, amount_sales, payment_s)
        VALUES (%s, %s, %s, %s)
    """, (name, datetime.now(), amount, payment))

    
    # reduce stock
    cursor.execute(
        "UPDATE products SET stock = stock - %s WHERE product_id = %s",
        (qty, product_id)
    )

    


    

    # check updated stock for debugging
    cursor.execute("SELECT stock FROM products WHERE product_id = %s", (product_id,))
    updated_stock = cursor.fetchone()

    db.commit()
   
    
    return jsonify({
        "status": "success",
        "product_id": product_id,
        "sold_qty": qty,
        "updated_stock": updated_stock[0] if updated_stock else None
    })



    



if __name__ == "__main__":
    app.run(debug=True, port=8000)

cursor.close()
db.close()    
