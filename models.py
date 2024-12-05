from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


db = SQLAlchemy()


# User model for authentication
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    superuser = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    data_centers = db.relationship(
        "DataCenter", secondary="user_data_center", backref="users", lazy="dynamic"
    )
    servers = db.relationship(
        "Server", secondary="user_server", backref="users", lazy="dynamic"
    )

    # Modify the get_servers method in your User model
    def get_servers(self):
        return self.servers

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "superuser": self.superuser,
            "role": self.role,
        }


user_data_center = db.Table(
    "user_data_center",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column(
        "data_center_id", db.Integer, db.ForeignKey("data_center.id"), primary_key=True
    ),
)


user_server = db.Table(
    "user_server",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("server_id", db.Integer, db.ForeignKey("server.id"), primary_key=True),
)


class DataCenter(db.Model):
    __tablename__ = "data_center"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    servers = relationship("Server", backref="data_center", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class Server(db.Model):
    __tablename__ = "server"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    data_center_id = db.Column(
        db.Integer, db.ForeignKey("data_center.id"), nullable=False
    )

    # Add cascade behavior for configs and vm_configs
    configs = db.relationship(
        "Config", backref="server", lazy=True, cascade="all, delete-orphan"
    )
    vm_configs = db.relationship(
        "VmConfig", backref="server", lazy=True, cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "data_center_id": self.data_center_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class Config(db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    meta_key = db.Column(db.String(64), nullable=False)
    meta_value = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    server_id = db.Column(db.Integer, db.ForeignKey("server.id"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "meta_key": self.meta_key,
            "meta_value": self.meta_value,
            "server_id": self.server_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class VmConfig(db.Model):
    __tablename__ = "vm_config"
    id = db.Column(db.Integer, primary_key=True)
    meta_key = db.Column(db.String(64), nullable=False)
    meta_value = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    server_id = db.Column(db.Integer, db.ForeignKey("server.id"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "meta_key": self.meta_key,
            "meta_value": self.meta_value,
            "server_id": self.server_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


def init_app(app):
    db.init_app(app)
