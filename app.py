from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)


# Define model class
class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")

        if not title or not desc:
            flash("Please fill in all fields", "error")
        else:
            # create a new record and add it into database
            todo = ToDo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()

            # flash a success message
            flash("Record added successfully", "success")

            # redirect to a route where you can display the flash message
            return redirect(url_for("home"))

    # retrieve data from the database
    todo = ToDo.query.all()
    return render_template("index.html", todo=todo)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_todo(id):
    # find record in database
    todo = ToDo.query.get_or_404(id)

    if request.method == "POST":
        try:
            db.session.delete(todo)
            db.session.commit()
            flash("Record deleted successfully", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting record: {str(e)}", "error")

    return redirect(url_for("home"))


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_todo(id):
    if request.method == "POST":
        title = request.form.get("new_title")
        desc = request.form.get("new_desc")

        # find todo item by id
        todo = ToDo.query.get_or_404(id)

        # update items
        if title is not None:
            todo.title = title

        if desc is not None:
            todo.desc = desc

        db.session.commit()
        flash("Todo item updated successfully", "success")
        return redirect(url_for("home"))

    todo = ToDo.query.get_or_404(id)
    # render the update form or template
    return render_template("update.html", todo=todo)


if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
