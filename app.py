from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="",
        database="",
        user="",
        password="YOUR_PASSWORD",
        port=""
    )

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM customer ORDER BY customer_id;")
    customers = cur.fetchall()

    cur.execute("SELECT * FROM restaurant ORDER BY restaurant_id;")
    restaurants = cur.fetchall()

    cur.execute("SELECT * FROM cuisine ORDER BY cuisine_id;")
    cuisines = cur.fetchall()

    cur.execute("SELECT * FROM restaurant_cuisine ORDER BY restaurant_id, cuisine_id;")
    restaurant_cuisines = cur.fetchall()

    cur.execute("""
    SELECT 
        f.customer_id,
        c.name AS customer_name,
        f.restaurant_id,
        r.name AS restaurant_name
    FROM favorite f
    JOIN customer c ON f.customer_id = c.customer_id
    JOIN restaurant r ON f.restaurant_id = r.restaurant_id
    ORDER BY f.customer_id, f.restaurant_id;
    """)
    favorites = cur.fetchall()

    cur.execute("SELECT * FROM orders ORDER BY order_id;")
    orders = cur.fetchall()

    cur.execute("SELECT * FROM review ORDER BY review_id;")
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        customers=customers,
        restaurants=restaurants,
        cuisines=cuisines,
        restaurant_cuisines=restaurant_cuisines,
        favorites=favorites,
        orders=orders,
        reviews=reviews
    )

@app.route("/add_customer", methods=["POST"])
def add_customer():
    name = request.form["name"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO customer (name) VALUES (%s);",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

@app.route("/delete_customer/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM customer WHERE customer_id = %s;",
        (customer_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

@app.route("/add_favorite", methods=["POST"])
def add_favorite():
    customer_id = request.form["customer_id"]
    restaurant_id = request.form["restaurant_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO favorite (customer_id, restaurant_id)
        VALUES (%s, %s)
        ON CONFLICT (customer_id, restaurant_id) DO NOTHING;
        """,
        (customer_id, restaurant_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")


@app.route("/delete_favorite/<int:customer_id>/<int:restaurant_id>", methods=["POST"])
def delete_favorite(customer_id, restaurant_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM favorite
        WHERE customer_id = %s AND restaurant_id = %s;
        """,
        (customer_id, restaurant_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)