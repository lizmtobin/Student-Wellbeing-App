from app import app, db
import os

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)
