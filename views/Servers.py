from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, Server, DataCenter, Config, VmConfig, User, user_server


servers = Blueprint('servers', __name__, template_folder='templates/servers', static_folder='static', url_prefix='/server')

@servers.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))

    # Assuming you have a User object representing the logged-in user
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        # Handle the case when the user is not found
        return render_template('error.html', error_message='User not found')
    
    if user.superuser:
        data_center_params = request.args.getlist('datacenter_id')
    
        if data_center_params:
            # If data_center_params is provided, filter servers based on the selected data centers
            servers = user.servers.filter(Server.data_center_id.in_(data_center_params)).all()
        else:
            # If no data_center_params provided, show all servers associated with the user
            servers = user.servers.all()
        # Retrieve data centers associated with the user
    data_centers = user.data_centers.all()

    data_center_params = request.args.getlist('datacenter_id')

    if data_center_params:
        # If data_center_params is provided, filter servers based on the selected data centers
        servers = user.servers.filter(Server.data_center_id.in_(data_center_params)).all()
    else:
        # If no data_center_params provided, show all servers associated with the user
        servers = user.servers.all()
    # Short servers by name
    servers.sort(key=lambda server: server.name)
    return render_template('servers.html', data_centers=data_centers, servers=servers)


@servers.route('/insert_server_form')
def insert_server_form():
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))
    datacenters = DataCenter.query.all()
    available_keys = Config.query.with_entities(Config.meta_key).distinct().all()
    available_keys = [key[0] for key in available_keys]
    available_keys.sort()
    available_values = Config.query.with_entities(Config.meta_value).distinct().filter(Config.meta_key != 'password').filter(Config.meta_key != 'idrac_password').all()
    available_values = [value[0] for value in available_values]
    available_values.sort()
    
    return render_template('insert-server-form.html', datacenters=datacenters, available_keys=available_keys, available_values=available_values)


@servers.route('/insert_server', methods=['POST'])
def insert_server():
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))
    try:
        server_name = request.form['server_name']
        server_ip = request.form['server_ip']
        data_center_id = request.form['data_center_id']
        config_keys = request.form.getlist('config_key[]')
        config_values = request.form.getlist('config_value[]')
        print(config_keys, config_values)
        server = Server(name=server_name, ip=server_ip, data_center_id=data_center_id)
        db.session.add(server)
        db.session.commit()
        for key, value in zip(config_keys, config_values):
            if key and value:  # Ensure key and value are not empty
                config = Config(meta_key=key, meta_value=value, server_id=server.id)
                db.session.add(config)

        # assign server to admin user
        admin = User.query.filter_by(username='admin').first()
        admin.servers.append(server)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error: ' + str(e))
    return redirect(url_for('servers.index'))


@servers.route('/update_server_form/<int:server_id>', methods=['GET'])
def update_server_form(server_id):
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))
    if request.method == 'GET':
        server = Server.query.filter_by(id=server_id).first()
        # get datacenter name
        datacenter = DataCenter.query.filter_by(id=server.data_center_id).first()
        server.data_center_name = datacenter.name
        # get config
        configs = Config.query.filter_by(server_id=server_id).all()
        server.configs = configs
        # get all datacenters
        datacenters = DataCenter.query.all()
        server.datacenter_name = datacenter.name
        available_keys = Config.query.with_entities(Config.meta_key).distinct().all()
        available_keys = [key[0] for key in available_keys]
        available_keys.sort()
        available_values = Config.query.with_entities(Config.meta_value).distinct().all()
        available_values = [value[0] for value in available_values]
        available_values.sort()
        return render_template('update-server-form.html', server=server, datacenters=datacenters, available_keys=available_keys, available_values=available_values)
    


@servers.route('/update_server', methods=['POST'])
def update_server():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        server_id = request.form.get('server_id')
        server = Server.query.get(server_id)

        if server:
            # Update server details
            server.name = request.form.get('name')
            server.ip = request.form.get('ip_address')
            server.data_center_id = request.form.get('datacenter')
            db.session.add(server)
            # Update existing configurations
            for i, config_id in enumerate(request.form.getlist('config_id[]')):
                config_key = request.form.getlist('config_key[]')[i]
                config_value = request.form.getlist('config_value[]')[i]
                config = Config.query.get(config_id)
                if config and config_key and config_value:
                    config.meta_key = config_key
                    config.meta_value = config_value

            # Delete configurations that are in the database but not in the form
            form_config_ids = set(map(int, request.form.getlist('config_id[]')))
            db_config_ids = {config.id for config in server.configs}
            configs_to_delete = db_config_ids - form_config_ids

            for config_id in configs_to_delete:
                config = Config.query.get(config_id)
                db.session.delete(config)
            # Add new configurations
            new_config_keys = request.form.getlist('new_config_key[]')
            new_config_values = request.form.getlist('new_config_value[]')
            for key, value in zip(new_config_keys, new_config_values):
                if key and value:
                    new_config = Config(meta_key=key, meta_value=value, server_id=server.id)
                    db.session.add(new_config)
            print(server.data_center_id)
            # Commit changes to the database
            db.session.commit()

    return redirect(url_for('servers.index'))




@servers.route('/show/<int:server_id>', methods=['GET'])
def show(server_id):
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))
    if request.method == 'GET':
        server = Server.query.filter_by(id=server_id).first()
        # get datacenter name
        datacenter = DataCenter.query.filter_by(id=server.data_center_id).first()
        server.data_center_name = datacenter.name
        # get config
        configs = Config.query.filter_by(server_id=server_id).all()
        server.configs = configs
        # get vm configs
        vm_configs = VmConfig.query.filter_by(server_id=server_id).all()
        # get vm os and unpack it
        return render_template('show_server.html', server=server, vm_configs=vm_configs)


@servers.route('/delete_server/<int:server_id>', methods=['GET'])
def delete_server(server_id):
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))

    server = Server.query.filter_by(id=server_id).first()
    if not server:
        return "Server not found", 404

    # Remove associations in user_server manually
    db.session.execute(
        user_server.delete().where(user_server.c.server_id == server_id)
    )
    db.session.delete(server)
    db.session.commit()

    return redirect(url_for('servers.index'))
