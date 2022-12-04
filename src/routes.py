from flask import render_template, redirect, url_for, request, flash, session
from repositories.note_repository import Note
from services.user_service import the_user_service
from services.note_service import the_note_service
from app import app
from util import validate_credentials


class CredentialsError(Exception):
    pass


def redirect_to_login():
    return redirect(url_for("login_page"))


def redirect_to_register():
    return redirect(url_for("register_page"))


def redirect_to_main():
    return redirect(url_for("main_page"))


@app.route("/", methods=["POST", "GET"])
def login_page():
    if request.method != "POST":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    try:
        if the_user_service.sign_in(username=username, password=password):
            session["username"] = username
            user_id = the_user_service.get_user_id_by_username(username)
            session["user_id"] = user_id
            return redirect_to_main()

        flash("Incorrect username or password")
    except CredentialsError as error:
        flash(str(error))

    return redirect_to_login()


@app.route("/register", methods=["POST", "GET"])
def register_page():
    if request.method != "POST":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]
    password_confirm = request.form["password_confirm"]

    issue = validate_credentials(username, password, password_confirm)
    if not issue is None:
        flash(issue)
        return redirect_to_register()

    try:
        if the_user_service.create_user(username=username, password=password):
            session["username"] = username
            user_id = the_user_service.get_user_id_by_username(username)
            session["user_id"] = user_id
            return redirect_to_main()
        else:
            flash("Username taken! Please choose another")
    except CredentialsError as error:
        flash(str(error))

    return redirect_to_register()


@app.route("/main", methods=["POST", "GET"])
def main_page():
    user = session["username"]
    user_id = session["user_id"]
    notes = the_note_service.get_all_notes_by_user_id(user_id)
    if request.method == "POST":
        return redirect_to_main()

    return render_template("note_listing.html", username=user, user_id=user_id, notes=notes)


@app.route("/create_note")
def create_note_page():
    if "username" not in session.keys():
        flash("Please sign in first")
        return redirect("/")
    return render_template("create_note.html")


@app.route("/create_new_note", methods=["POST", "GET"])
def create_new_reference():
    note = Note(
        author = request.form["author"],
        title = request.form["title"],
        year = request.form["year"],
        doi_address = request.form["doi_address"],
        bib_category = request.form["bib_category"],
        bib_citekey = request.form["bib_citekey"],
    )
    user_id = session["user_id"]

    creation = the_note_service.create_note(user_id, note)
    if creation:
        flash("New reference created successfully!")
        return redirect("/create_note")
    else:
        flash("Something went wrong")
        return redirect("/create_note")

