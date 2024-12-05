from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.security import generate_password_hash
from models import User, DataCenter, Server, db

users = Blueprint(
    "users",
    __name__,
    template_folder="templates/users",
    static_folder="static",
    url_prefix="/user",
)


@users.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    all_users = User.query.all()
    users = User.query.filter_by(superuser=False).all()

    return render_template("users.html", users=users, all_users=all_users)


@users.route("/add_user_form")
def add_user_form():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))

    data_centers_servers = {}

    data_centers = DataCenter.query.all()
    for data_center in data_centers:
        data_centers_servers[data_center.id] = {}
        data_centers_servers[data_center.id]["data_center"] = (
            data_center.serialize()
        )  # Serialize DataCenter
        data_centers_servers[data_center.id]["servers"] = [
            server.serialize()
            for server in Server.query.filter_by(data_center_id=data_center.id).all()
        ]

    users = User.query.all()

    return render_template(
        "add_user.html", data_centers_servers=data_centers_servers, users=users
    )


@users.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        user_id = request.form.get("username")
        password = request.form.get("password")
        superuser = int(request.form.get("superuser"))
        password_hash = generate_password_hash(password)
        data_center_id = request.form.get("data_center_id")
        server_ids = request.form.getlist("server_ids[]")

        # Check if the user already exists
        existing_user = User.query.filter_by(username=user_id).first()
        if existing_user:
            flash("User already exists. Please choose a different username.")
            return redirect(url_for("users.index"))

        new_user = User(
            username=user_id, password=password_hash, superuser=superuser, role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        # Fetch the user from the database after committing to get the ID
        user = User.query.filter_by(username=user_id).first()

        if not user or not data_center_id:
            flash("Please select user, data center, and servers")
            return redirect(url_for("users.index"))

        data_center = DataCenter.query.get(data_center_id)

        if server_ids == ["all"]:
            for server in data_center.servers:
                if data_center not in user.data_centers:
                    user.data_centers.append(data_center)
                if server not in user.servers:
                    user.servers.append(server)
            db.session.commit()
            return redirect(url_for("users.index"))

        if data_center:
            if data_center not in user.data_centers:
                user.data_centers.append(data_center)
            db.session.commit()

        for server_id in server_ids:
            server = Server.query.get(server_id)
            if server and server not in user.servers:
                user.servers.append(server)

        db.session.commit()

        return redirect(url_for("users.index"))

    return render_template("users/add_user.html")


@users.route("/edit_user_form/<int:user_id>")
def edit_user_form(user_id):
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))

    user = User.query.get(user_id)
    data_centers_servers = {}

    data_centers = DataCenter.query.all()
    for data_center in data_centers:
        data_centers_servers[data_center.id] = {}
        data_centers_servers[data_center.id]["data_center"] = data_center
        data_centers_servers[data_center.id]["servers"] = Server.query.filter_by(
            data_center_id=data_center.id
        ).all()
    for data_center_id in data_centers_servers:
        for server in data_centers_servers[data_center_id]["servers"]:
            server.serialize()
    return render_template(
        "edit_user.html", user=user, data_centers_servers=data_centers_servers
    )


@users.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    if request.method == "POST":
        user = User.query.get(user_id)
        username = request.form.get("username")
        if username:
            if username == user.username:
                pass
            else:
                user.username = username
        superuser = int(request.form.get("superuser"))
        if superuser:
            user.superuser = superuser
        password = request.form.get("password")
        if password:
            password_hash = generate_password_hash(password)
            user.password = password_hash
        db.session.commit()
        data_center_id = request.form.get("data_center_id")
        server_ids = request.form.getlist("server_ids[]")
        if data_center_id and server_ids:
            # check if the user already has the data center
            data_center = DataCenter.query.get(data_center_id)
            if data_center not in user.data_centers:
                user.data_centers.append(data_center)
                db.session.commit()
            # check if the user already has the servers
            if server_ids == ["all"]:
                for server in data_center.servers:
                    if server not in user.servers:
                        user.servers.append(server)
                db.session.commit()
                return redirect(url_for("users.index"))
            for server_id in server_ids:
                server = Server.query.get(server_id)
                if server not in user.servers:
                    user.servers.append(server)
                    db.session.commit()
        return redirect(url_for("users.index"))
    return render_template("edit_user.html")


@users.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    # delete user and data center association and server association
    user = User.query.get(user_id)
    data_centers = user.data_centers.all()
    servers = user.servers.all()
    for data_center in data_centers:
        user.data_centers.remove(data_center)
    for server in servers:
        user.servers.remove(server)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("users.index"))


@users.route("/users.delete_server/<int:user_id>/<int:server_id>")
def delete_server(user_id, server_id):
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    user = User.query.get(user_id)
    server = Server.query.get(server_id)
    user.servers.remove(server)
    db.session.commit()
    return redirect(url_for("users.index"))
