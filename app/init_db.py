import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vshop.db")
if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)
c = con.cursor()
c.executescript("""
DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders; DROP TABLE IF EXISTS reviews;
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, role TEXT, avatar TEXT, reset_token TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, description TEXT, image TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, items TEXT, total REAL, status TEXT, card TEXT);
CREATE TABLE reviews (id INTEGER PRIMARY KEY, product_id INTEGER, user_id INTEGER, comment TEXT);
""")

# 20 demo users
users = [
    ("arjun01","Arjun@123","arjun01@vshop.in"),("rohit02","Rohit@456","rohit02@vshop.in"),
    ("priya03","Priya@789","priya03@vshop.in"),("neha04","Neha@321","neha04@vshop.in"),
    ("karan05","Karan@654","karan05@vshop.in"),("ananya06","Ananya@987","ananya06@vshop.in"),
    ("rahul07","Rahul@147","rahul07@vshop.in"),("sneha08","Sneha@258","sneha08@vshop.in"),
    ("vikas09","Vikas@369","vikas09@vshop.in"),("pooja10","Pooja@741","pooja10@vshop.in"),
    ("amit11","Amit@852","amit11@vshop.in"),("kavya12","Kavya@963","kavya12@vshop.in"),
    ("ajay13","Ajay@159","ajay13@vshop.in"),("divya14","Divya@357","divya14@vshop.in"),
    ("nikhil15","Nikhil@486","nikhil15@vshop.in"),("meera16","Meera@753","meera16@vshop.in"),
    ("yash17","Yash@951","yash17@vshop.in"),("rhea18","Rhea@246","rhea18@vshop.in"),
    ("sameer19","Sameer@578","sameer19@vshop.in"),("aditi20","Aditi@834","aditi20@vshop.in"),
]
for u, p, e in users:                                     # FIXED: 5 columns, 5 values
    c.execute("INSERT INTO users (username,password,email,role,avatar,reset_token) VALUES (?,?,?,?,NULL,NULL)", (u, p, e, "user"))
# admin — default creds (intentional vuln)
c.execute("INSERT INTO users (username,password,email,role,avatar,reset_token) VALUES ('admin','admin123','admin@vshop.in','admin',NULL,NULL)")

# 20 products — name, category, price (₹)
products = [
    ("Wireless Headphones","Electronics",2499.00),("Smart Watch","Electronics",4999.00),
    ("Mechanical Keyboard","Electronics",3499.00),("Bluetooth Speaker","Electronics",1799.00),
    ("USB-C Hub","Electronics",1299.00),
    ("T-Shirt","Fashion",499.00),("Hoodie","Fashion",1199.00),("Jeans","Fashion",1499.00),
    ("Running Shoes","Fashion",2299.00),("Backpack","Fashion",899.00),
    ("Desk Lamp","Home & Living",699.00),("Coffee Maker","Home & Living",2899.00),
    ("Water Bottle","Home & Living",399.00),("Table Organizer","Home & Living",549.00),
    ("LED Light","Home & Living",299.00),
    ("Sunglasses","Accessories",799.00),("Wallet","Accessories",649.00),
    ("Phone Case","Accessories",349.00),("Watch Strap","Accessories",449.00),
    ("Laptop Sleeve","Accessories",599.00),
]
for i, (n, cat, price) in enumerate(products, 1):
    c.execute("INSERT INTO products VALUES (?,?,?,?,?,?)",
              (i, n, cat, price, f"Premium quality {n.lower()}. Ships in 2-3 days with 1-year warranty.", f"p{i}.jpg"))

# sample orders (for IDOR testing) + one review (for stored XSS testing)
c.execute("INSERT INTO orders (user_id,items,total,status,card) VALUES (1,'Wireless Headphones x1',2499.0,'Shipped','4111-1111-1111-1111')")
c.execute("INSERT INTO orders (user_id,items,total,status,card) VALUES (2,'Backpack x2',1798.0,'Pending','5500-0000-0000-0004')")
c.execute("INSERT INTO orders (user_id,items,total,status,card) VALUES (3,'Coffee Maker x1',2899.0,'Shipped','6011-1111-1111-1117')")
c.execute("INSERT INTO reviews (product_id,user_id,comment) VALUES (1,3,'Great sound quality, worth the price!')")

con.commit(); con.close()
print(f"[+] Database created: {DB}")
print(f"[+] Users: 20 demo + 1 admin  |  Products: 20  |  Orders: 3")
