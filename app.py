
from flask import Flask, render_template, request, redirect, flash
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","cps-secret")

TOPICS = [
"Topic 1 - Introduction & Steam Power Plant Overview",
"Topic 2 - Boiler System",
"Topic 3 - Boiler Auxiliaries",
"Topic 4 - Steam Turbine System",
"Topic 5 - Turbine Auxiliaries & Oil Systems",
"Topic 6 - Electrical Systems",
"Topic 7 - Instrumentation & Control",
"Topic 8 - Water Treatment & Chemistry",
"Topic 9 - Plant Operation & Summary"
]

def conn():
    c = sqlite3.connect("lottery.db")
    c.row_factory = sqlite3.Row
    return c

def init_db():
    db=conn()
    db.execute('CREATE TABLE IF NOT EXISTS allocations(student TEXT UNIQUE, topic TEXT UNIQUE)')
    db.commit()
    db.close()

init_db()

@app.route("/")
def home():
    db=conn()
    rows=db.execute("SELECT * FROM allocations ORDER BY student").fetchall()
    db.close()
    return render_template("index.html", allocations=rows, remaining=len(TOPICS)-len(rows))

@app.post("/draw")
def draw():
    name=request.form.get("student","").strip()
    if not name:
        flash("Please enter a name.")
        return redirect("/")

    db=conn()
    existing=db.execute("SELECT * FROM allocations WHERE lower(student)=lower(?)",(name,)).fetchone()
    if existing:
        flash(f"{existing['student']} already received: {existing['topic']}")
        db.close()
        return redirect("/")

    used=[r["topic"] for r in db.execute("SELECT topic FROM allocations")]
    available=[t for t in TOPICS if t not in used]

    if not available:
        flash("All topics have been allocated.")
        db.close()
        return redirect("/")

    topic=random.choice(available)
    db.execute("INSERT INTO allocations(student,topic) VALUES(?,?)",(name,topic))
    db.commit()
    db.close()

    flash(f"{name} received: {topic}")
    return redirect("/")

@app.post("/admin/reset")
def reset():
    if request.form.get("password") != "CUET2026":
        flash("Invalid admin password.")
        return redirect("/")
    db=conn()
    db.execute("DELETE FROM allocations")
    db.commit()
    db.close()
    flash("Lottery reset completed.")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
