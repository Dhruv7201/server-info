from flask import Blueprint, request, redirect, url_for,  session, jsonify
from models import db, Config, DataCenter, Server, User, VmConfig
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta


configs = Blueprint('configs', __name__, template_folder='templates/configs', static_folder='static', url_prefix='/config')


@configs.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('index.main'))

    # Assuming you have a User object representing the logged-in user
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        # Handle the case when the user is not found
        return jsonify({'error': 'User not found'})

    # Retrieve data centers and servers associated with the user
    datacenters = user.data_centers.all()
    servers = user.servers.all()

    filters = {}

    # Add data centers to filters
    list_datacenters = [datacenter.name for datacenter in datacenters]
    filters['datacenter'] = list_datacenters

    # Query configurations associated with the user's servers
    configs = Config.query.filter(Config.server_id.in_([server.id for server in servers])).order_by(Config.meta_key).all()
    vm_configs = VmConfig.query.filter(VmConfig.server_id.in_([server.id for server in servers])).order_by(VmConfig.meta_key).all()
    key_list = sorted({config.meta_key for config in configs})
    key_list.extend(sorted({config.meta_key for config in vm_configs}))
    for key in key_list:
        # take values only associated with the user servers
        filters[key] = filters[key] = sorted({config.meta_value for config in configs if config.meta_key == key})

        filters[key].extend(sorted({config.meta_value for config in vm_configs if config.meta_key == key}))
        # remove duplicates
        filters[key] = list(dict.fromkeys(filters[key]))

    
    # add ip from servers
    filters['IP'] = sorted({server.ip for server in servers})
    for key in sorted(filters.keys()):
        if key == 'datacenter':
            continue
    
    if not filters[key]:
        filters.pop(key, None)
        filters.pop('IP', None)
    filters.pop('password', None)
    filters.pop('idrac_password', None)

    return jsonify(filters)




@configs.route('/filter', methods=['POST'])
def filter():
    selected_values = request.get_json()
    server_list = []

    # Original list of servers
    user = User.query.filter_by(username=session.get('username')).first()
    servers = user.servers

    # Filter based on last_updated_at
    if 'last_updated_at' in selected_values:
        if selected_values['last_updated_at'] != 'None':
            hours = 24
            if '24hours' in selected_values['last_updated_at']:
                hours = 24
            elif '1week' in selected_values['last_updated_at']:
                hours = 7 * 24
            elif '1month' in selected_values['last_updated_at']:
                hours = 30 * 24
            elif '1year' in selected_values['last_updated_at']:
                hours = 365 * 24

            servers = servers.filter(Server.updated_at > datetime.now() - timedelta(hours=hours))
        selected_values.pop('last_updated_at')

    # Filter based on datacenter
    if 'datacenter' in selected_values:
        datacenter_ids = [DataCenter.query.filter_by(name=datacenter).first().id for datacenter in selected_values['datacenter']]
        servers = servers.filter(Server.data_center_id.in_(datacenter_ids))
        selected_values.pop('datacenter')

    # Filter based on meta key and value
    query_filters = []
    for meta_key, meta_values in selected_values.items():
        if 'datacenter' != meta_key:
            # Create alias for Config and VmConfig to avoid conflicts in the query
            config_alias = aliased(Config)
            vm_config_alias = aliased(VmConfig)

            # Use outerjoin to handle relationships
            servers = servers.outerjoin(config_alias, Server.id == config_alias.server_id)\
                             .outerjoin(vm_config_alias, Server.id == vm_config_alias.server_id)

            # Apply filter conditions
            query_filters.append(or_(
                and_(config_alias.meta_key == meta_key, config_alias.meta_value.in_(meta_values)),
                and_(vm_config_alias.meta_key == meta_key, vm_config_alias.meta_value.in_(meta_values))
            ))
    # also search in server table for selected values
    if 'IP' in selected_values:
        # search for ip in server table if found then add to query_filters
        query_filters.append(Server.ip.in_(selected_values['IP']))


    if query_filters:
        servers = servers.filter(or_(*query_filters))

    server_list = servers.all()

    server_list.sort(key=lambda x: x.name)
    
    return jsonify([server.serialize() for server in server_list])
