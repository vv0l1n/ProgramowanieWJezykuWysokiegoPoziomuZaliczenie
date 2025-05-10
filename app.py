from datetime import datetime, timezone

from flask import render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms import LoginForm, AddCarForm, RegistrationForm
from helpers import create_app
from models import db, User, Car, Rental

db, app = create_app(db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('user_panel'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    form = AddCarForm()
    cars = Car.query.all()

    if form.validate_on_submit():
        new_car = Car(
            brand=form.brand.data,
            model=form.model.data,
            is_rented=False
        )
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for('admin_panel'))

    return render_template('admin_panel.html', cars=cars, form=form)

@app.route('/admin/delete_car/<int:car_id>')
@login_required
def delete_car(car_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    car = Car.query.get(car_id)
    db.session.delete(car)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_car/<int:car_id>', methods=['POST'])
@login_required
def edit_car(car_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    car = Car.query.get(car_id)
    car.brand = request.form['brand']
    car.model = request.form['model']
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/users')
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>')
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_details.html', user=user)

@app.route('/user')
@login_required
def user_panel():
    available_cars = Car.query.filter_by(is_rented=False).all()
    rented_cars = Car.query.filter_by(rented_by=current_user.id).all()
    return render_template('user_panel.html', cars=available_cars, rented_cars=rented_cars)


@app.route('/rent/<int:car_id>')
@login_required
def rent_car(car_id):
    car = Car.query.get(car_id)
    if car and not car.is_rented:
        car.is_rented = True
        car.rented_by = current_user.id
        rental = Rental(user_id=current_user.id, car_id=car.id, rental_date=datetime.utcnow())
        db.session.add(rental)
        db.session.commit()
    return redirect(url_for('user_panel'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already taken')
            return redirect(url_for('register'))
        new_user = User(username=form.username.data, role='user')
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/return_car/<int:car_id>')
@login_required
def return_car(car_id):
    car = Car.query.get(car_id)
    if car and car.rented_by == current_user.id:
        car.is_rented = False
        car.rented_by = None
        rental = Rental.query.filter_by(car_id=car.id, user_id=current_user.id, return_date=None).first()
        if rental:
            rental.return_date = datetime.utcnow()
            db.session.commit()
    return redirect(url_for('user_panel'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
