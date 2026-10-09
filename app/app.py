import sqlite3, os, subprocess, requests as req
from flask import Flask, request, session, redirect, url_for, render_template, render_template_string, abort, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "vshop.db")
app = Flask(__name__)
app.secret_key = "vshop-secret-123"                       # [VULN-12] hardcoded weak secret
app.config["DEBUG"] = True                                # [VULN-11] debugger + verbose errors

def db(): return sqlite3.connect(DB)

def waf(s):                                               # [VULN-1b] naive blocklist WAF — bypassable
    bad = ["or", "and", "union select", "select", "from", "where", "--", ";", "1=1"]
    for b in bad:
        if b in s.lower(): abort(403, "WAF: suspicious keyword blocked")

# ---------- STORE ----------
@app.route("/")
def home():
    q = request.args.get("q", "")
    prods = None
    if q:
        waf(q)                                            # [VULN-1b]
        con = db()
        prods = con.execute(f"SELECT * FROM products WHERE name LIKE '%{q}%'").fetchall()   # [VULN-1] SQLi
        con.close()
    con = db(); all_p = con.execute("SELECT * FROM products").fetchall(); con.close()
    return render_template("index.html", products=(prods if prods is not None else all_p), q=q)

@app.route("/product/<pid>")
def product(pid):
    waf(pid)
    con = db()
    p = con.execute(f"SELECT * FROM products WHERE id = {pid}").fetchone()                  # [VULN-1] SQLi
    revs = con.execute("SELECT r.comment,u.username FROM reviews r LEFT JOIN users u ON r.user_id=u.id WHERE r.product_id=?",(pid,)).fetchall()
    con.close()
    if not p: return render_template_string("<h2>Product not found</h2>"), 404
    return render_template("product.html", p=p, reviews=revs)

@app.route("/review/<pid>", methods=["POST"])
def review(pid):
    if "uid" not in session: return redirect("/login")
    con = db()
    con.execute("INSERT INTO reviews (product_id,user_id,comment) VALUES (?,?,?)",
                (pid, session["uid"], request.form["comment"]))                                # [VULN-3] stored XSS
    con.commit(); con.close()
    return redirect(f"/product/{pid}")

# ---------- AUTH ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        con = db()
        con.execute("INSERT INTO users (username,password,email,role) VALUES (?,?,?,'user')",
                    (request.form["u"], request.form["p"], request.form["e"]))                 # [VULN-4] plaintext pw
        con.commit(); con.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    err = ""
    if request.method == "POST":
        u, p = request.form["u"], request.form["p"]
        con = db()
        row = con.execute(f"SELECT id,username,role FROM users WHERE username='{u}' AND password='{p}'").fetchone()   # [VULN-1] SQLi login
        con.close()
        if row:
            session["uid"], session["u"], session["role"] = row
            return redirect("/")
        err = "Invalid credentials"                                                            # [VULN-5] no lockout
    return render_template("login.html", err=err)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(request.args.get("next", "/"))                                             # [VULN-10b] open redirect

# ---------- USER ----------
@app.route("/profile", methods=["GET","POST"])
def profile():
    if "uid" not in session: return redirect("/login")
    msg = ""
    if request.method == "POST":
        con = db()
        con.execute("UPDATE users SET email=? WHERE id=?", (request.form["email"], session["uid"]))
        con.commit(); con.close()                                                              # [VULN-7] CSRF
        msg = "Email updated successfully"
    con = db(); u = con.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone(); con.close()
    return render_template("profile.html", u=u, msg=msg)

@app.route("/avatar", methods=["POST"])
def avatar():
    if "uid" not in session: return abort(401)
    f = request.files["file"]
    path = os.path.join(BASE, "static", "uploads", f.filename)                                 # [VULN-8] unrestricted upload
    f.save(path)
    return f"Uploaded: <a href='/static/uploads/{f.filename}'>{f.filename}</a>"

@app.route("/static/uploads/")
@app.route("/static/uploads")
def uploads_list():                                                                            # [VULN-11b] directory listing
    entries = os.listdir(os.path.join(BASE, "static", "uploads"))
    return "<h2>Uploads</h2><br>" + "<br>".join(entries) or "empty"

# ---------- CART / PAYMENT / ORDERS ----------
@app.route("/cart", methods=["GET","POST"])
def cart():
    cart = session.get("cart", [])
    if request.method == "POST":
        pid = int(request.form["pid"])
        qty = int(request.form["qty"])                                                         # [VULN-6b] negative qty
        price = float(request.form.get("price", 0))                                            # [VULN-6] client price
        name = request.form.get("name", "?")
        cart.append({"pid":pid,"qty":qty,"price":price,"name":name})
        session["cart"] = cart
    total = sum(i["price"]*i["qty"] for i in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/payment", methods=["GET"])                                                        # FIX: was missing → 404
def payment():
    if "uid" not in session: return redirect("/login")
    cart = session.get("cart", [])
    if not cart: return redirect("/cart")
    total = sum(i["price"]*i["qty"] for i in cart)
    return render_template("payment.html", total=total)

@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", [])
    if not cart or "uid" not in session: return redirect("/cart")
    total = sum(i["price"]*i["qty"] for i in cart)                                             # [VULN-6] tampered totals trusted
    con = db()
    con.execute("INSERT INTO orders (user_id,items,total,status,card) VALUES (?,?,?,?,?)",
                (session["uid"], ", ".join(f"{i['name']} x{i['qty']}" for i in cart),
                 total, "Pending", request.form.get("card", "")))
    oid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    con.commit(); con.close()
    session["cart"] = []
    return redirect(f"/order-success/{oid}")

@app.route("/order-success/<int:oid>")                                                         # FIX: was missing → 404
def order_success(oid):
    return render_template("order_success.html", oid=oid)

@app.route("/orders")
def orders():
    if "uid" not in session: return redirect("/login")
    con = db(); rows = con.execute("SELECT * FROM orders WHERE user_id=?", (session["uid"],)).fetchall(); con.close()
    return render_template("orders.html", orders=rows)

@app.route("/order/<int:oid>")
def order(oid):                                                                                # [VULN-2] IDOR
    con = db(); o = con.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone(); con.close()
    if not o: abort(404)
    return render_template("order.html", o=o)

@app.route("/invoice/<int:oid>")                                                               # [VULN-2] IDOR #2
def invoice(oid):
    con = db(); o = con.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone(); con.close()
    return render_template_string(f"<h1>Invoice #{oid}</h1><pre>{o}</pre>")

# ---------- TOOLS PAGES ----------
@app.route("/check-pincode", methods=["GET","POST"])
def pincode():
    out = ""
    if request.method == "POST":
        pin = request.form["pin"]
        out = subprocess.getoutput(f"curl -s --max-time 2 http://pincode-api.internal.local/lookup?pin={pin}")   # [VULN-13] cmd injection
    return render_template_string("""<h2>Check Delivery / Pincode</h2>
      <form method=post><input name=pin placeholder='e.g. 110001'><button>Check</button></form>
      <pre>{{out}}</pre>""", out=out)

@app.route("/import-product")
def import_product():
    url = request.args.get("url")
    data = err = None
    if url:
        try: data = req.get(url, timeout=3, verify=False).text[:2000]                          # [VULN-10] SSRF
        except Exception as e: err = str(e)
    return render_template("import_product.html", data=data, err=err, url=url)

@app.route("/api/users")                                                                       # [VULN-11c] data leak
def api_users():
    con = db(); rows = con.execute("SELECT id,username,password,email,role,reset_token FROM users").fetchall(); con.close()
    keys = ["id","username","password","email","role","reset_token"]
    return {"users":[dict(zip(keys,r)) for r in rows]}

# ---------- ADMIN ----------
def is_admin():
    if session.get("role") == "admin": return True
    ip = request.remote_addr
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd: ip = fwd.split(",")[0]                                                             # [VULN-9b] 403 bypass via header
    return ip == "127.0.0.1"

@app.route("/admin")
def admin():
    if not is_admin(): abort(403)
    con = db(); us = con.execute("SELECT id,username,email,role FROM users").fetchall()
    os_ = con.execute("SELECT * FROM orders").fetchall(); con.close()
    return render_template("admin.html", users=us, orders=os_)

@app.route("/admin/product/add", methods=["POST"])                                             # [VULN-5] no admin check at all
def admin_add():
    con = db()
    con.execute("INSERT INTO products (name,category,price,description,image) VALUES (?,?,?,?,?)",
                (request.form["name"], request.form["cat"], request.form["price"], request.form["desc"], ""))
    con.commit(); con.close()
    return "Product added (endpoint had NO admin check!)"

@app.route("/admin/product/delete/<pid>", methods=["POST","GET"])
def admin_del(pid):
    if not is_admin(): abort(403)
    con = db(); con.execute("DELETE FROM products WHERE id=?", (pid,)); con.commit(); con.close()
    return redirect("/admin")

@app.errorhandler(500)
def e500(e):
    import traceback
    return f"<h1>500</h1><pre>{traceback.format_exc()}</pre>", 500                              # [VULN-11] stack trace leak

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
