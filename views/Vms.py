from flask import Blueprint, render_template, redirect, url_for, session, request
from models import VmConfig, db


vms = Blueprint(
    "vms",
    __name__,
    template_folder="templates/vms",
    static_folder="static",
    url_prefix="/vm",
)


@vms.route("/insert_vm_form", methods=["GET", "POST"])
def insert_vm_form():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    server_id = request.args.get("server_id")
    available_keys = VmConfig.query.with_entities(VmConfig.meta_key).distinct().all()
    available_keys = [key[0] for key in available_keys]
    available_keys.sort()
    available_values = (
        VmConfig.query.with_entities(VmConfig.meta_value).distinct().all()
    )
    available_values = [value[0] for value in available_values]
    available_values.sort()

    return render_template(
        "insert_vm_form.html",
        available_keys=available_keys,
        available_values=available_values,
        server_id=server_id,
    )


@vms.route("/insert_vm", methods=["POST"])
def insert_vm():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    server_id = request.form.get("server_id")
    config_keys = request.form.getlist("config_key[]")
    config_values = request.form.getlist("config_value[]")
    for key, value in zip(config_keys, config_values):
        if key and value:  # Ensure key and value are not empty
            vm_config = VmConfig(meta_key=key, meta_value=value, server_id=server_id)
            db.session.add(vm_config)
    db.session.commit()

    return redirect(url_for("servers.show", server_id=server_id))


@vms.route("/update_vm_form", methods=["GET", "POST"])
def update_vm_form():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))
    server_id = request.args.get("server_id")
    existing_vm_configs = VmConfig.query.filter_by(server_id=server_id).all()
    available_keys = VmConfig.query.with_entities(VmConfig.meta_key).distinct().all()
    available_keys = [key[0] for key in available_keys]
    available_keys.sort()
    available_values = (
        VmConfig.query.with_entities(VmConfig.meta_value).distinct().all()
    )
    available_values = [value[0] for value in available_values]
    available_values.sort()
    return render_template(
        "update_vm_form.html",
        existing_vm_configs=existing_vm_configs,
        available_keys=available_keys,
        available_values=available_values,
        server_id=server_id,
    )


@vms.route("/update_vm", methods=["POST"])
def update_vm():
    if not session.get("logged_in"):
        return redirect(url_for("index.main"))

    server_id = request.form.get("server_id")

    # Delete all existing vm configs
    VmConfig.query.filter_by(server_id=server_id).delete()
    db.session.commit()

    # Insert new vm configs
    config_keys = request.form.getlist("meta_key[]")
    config_values = request.form.getlist("meta_value[]")
    print(config_keys, config_values)
    for key, value in zip(config_keys, config_values):
        print(key, value)
        if key and value:
            print(key, value)
            vm_config = VmConfig(meta_key=key, meta_value=value, server_id=server_id)
            db.session.add(vm_config)
    new_config_keys = request.form.getlist("new_meta_key[]")
    new_config_values = request.form.getlist("new_meta_value[]")
    for key, value in zip(new_config_keys, new_config_values):
        if key and value:
            vm_config = VmConfig(meta_key=key, meta_value=value, server_id=server_id)
            db.session.add(vm_config)
    db.session.commit()

    return redirect(url_for("servers.show", server_id=server_id))
