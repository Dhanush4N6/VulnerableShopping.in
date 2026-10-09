@app.route("/order-success/<int:oid>")
def order_success(oid):
    return render_template("order_success.html", oid=oid)
