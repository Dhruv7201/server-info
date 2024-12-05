from views.DataCenter import datacenter
from views.Servers import servers
from views.Index import index
from views.Configs import configs
from views.Vms import vms
from views.Users import users


# Register all blueprints
def register_blueprints(app):
    app.register_blueprint(index)
    app.register_blueprint(datacenter)
    app.register_blueprint(servers)
    app.register_blueprint(configs)
    app.register_blueprint(vms)
    app.register_blueprint(users)
