from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.user import User
from flask_app.models.show import Show
from flask import flash

@app.route("/shows/home")
def sightings_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    shows = Show.get_all()

    return render_template("home.html", user=user, shows=shows)

@app.route("/shows/<int:show_id>")
def show_detail(show_id):
    user = User.get_by_id(session["user_id"])
    show = Show.get_by_id(show_id)
    return render_template("show_detail.html", user=user, show=show)

@app.route("/shows/create")
def show_create_page():
    user = User.get_by_id(session["user_id"])
    return render_template("create_show.html", user = user)

@app.route("/shows/edit/<int:show_id>")
def show_edit_page(show_id):
    user = User.get_by_id(session["user_id"])
    show = Show.get_by_id(show_id)
    return render_template("edit_show.html",  user = user, show = show)

@app.route("/shows", methods=["POST"])
def create_show():
    valid_show = Show.create_valid_show(request.form)
    if valid_show:
        return redirect(f'/shows/{valid_show.id}')
    return redirect('/shows/create')

@app.route("/shows/<int:show_id>", methods=["POST"])
def update_show(show_id):

    valid_show = Show.update_show(request.form, session["user_id"])

    if not valid_show:
        return redirect(f"/shows/edit/{show_id}")
        
    return redirect(f"/shows/{show_id}")

@app.route("/shows/delete/<int:show_id>")
def delete_by_id(show_id):
    Show.delete_show_by_id(show_id)
    return redirect("/shows/home")