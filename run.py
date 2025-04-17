from app import app, db

if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()