# views/DataCenter.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, DataCenter, User


datacenter = Blueprint(
    "datacenter",
    __name__,
    template_folder="templates/datacenter",
    static_folder="static",
    url_prefix="/datacenter",
)


@datacenter.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))

    # Assuming you have a User object representing the logged-in user
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    if user.superuser:
        datacenters = DataCenter.query.all()
        # short based on name
        datacenters.sort(key=lambda x: x.name)

        return render_template("datacenter.html", datacenters=datacenters)
    if not user:
        # Handle the case when the user is not found
        return render_template("error.html", error_message="User not found")

    # Retrieve data centers associated with the user
    datacenters = user.data_centers.all()

    return render_template("datacenter.html", datacenters=datacenters)


@datacenter.route("/insert_datacenter_form")
def insert_datacenter_form():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    return render_template("insert_datacenter_form.html")


@datacenter.route("/insert_datacenter", methods=["POST"])
def insert_datacenter():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    datacenter_name = request.form["datacenter_name"]
    datacenter_location = request.form["datacenter_location"]
    datacenter = DataCenter(name=datacenter_name, location=datacenter_location)
    db.session.add(datacenter)
    # add data center to the admin user
    admin = User.query.filter_by(username="admin").first()
    admin.data_centers.append(datacenter)
    db.session.commit()
    flash("Data Center inserted successfully")
    return redirect(url_for("datacenter.index"))
