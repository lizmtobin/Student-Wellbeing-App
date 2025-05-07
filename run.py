from app import app, db
from app.debug_utils import reset_db
import os

def init_db():
    print("\n=== Starting Database Initialization ===")
    # Remove existing database file if it exists
    db_path = os.path.join(app.root_path, 'data', 'data.sqlite')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✓ Removed existing database file")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    print("✓ Data directory ready")
    
    # Create tables and seed data
    print("\nCreating database tables...")
    db.create_all()
    print("✓ Database tables created")
    
    print("\nSeeding database with initial data...")
    reset_db()
    print("\n=== Database Initialization Complete ===\n")

# Initialize database before starting Flask
with app.app_context():
    init_db()

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)
