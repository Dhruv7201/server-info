# run.py
import os
from models import db
from flask import Flask
from sqlalchemy import text
from dotenv import load_dotenv
from Blueprints import register_blueprints
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
db.init_app(app)


with app.app_context():
    try:
        # Create tables
        db.create_all()

        # Generate a hashed password
        password = "admin"
        hashed_password = generate_password_hash(password)

        # Call the stored procedure with the hashed password
        query = text("CALL CreateAdminUser(:hashed_password)")
        db.session.execute(query, {"hashed_password": hashed_password})
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
