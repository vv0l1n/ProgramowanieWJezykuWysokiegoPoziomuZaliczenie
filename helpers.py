from flask import Flask

from models import User


def create_tables_and_admin(app, db):
    if not hasattr(app, 'db_initialized'):
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        app.db_initialized = True

def create_app(db):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:7890/car_rent'

    db.init_app(app)

    with app.app_context():
        create_tables_and_admin(app, db)

    return db, app