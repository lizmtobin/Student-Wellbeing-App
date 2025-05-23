from flask import Flask
from config import Config
from jinja2 import StrictUndefined
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_migrate import Migrate

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

from app import views, models
from app.debug_utils import reset_db

@app.cli.command("seed-db")
def seed_db_command():
    """Seed the database with test data."""
    print("Seeding database...")
    reset_db()
    print("Database seeded successfully!")

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)
