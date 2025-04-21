from flask import Flask ,render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app)

class Driver(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)  # This defines the primary key
    name = db.Column(db.String(50), nullable=False)#whether a field can be empty or have value
    phone = db.Column(db.Integer,nullable=False)
    vh_type=db.Column(db.String(10))
    vh_no=db.Column(db.String(15))
    pickup=db.Column(db.String(20),nullable=False)
    avail=db.Column(db.Boolean,default=True)

class Customer(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)  # This defines the primary key
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    pickup=db.Column(db.String(20),nullable=False)
    avail=db.Column(db.Boolean,default=True)

with app.app_context():
    db.create_all()  

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/ctride',methods=['GET','POST'])
def ctride():
    print(request.method)
    if request.method == 'POST':
        name = request.form.get('un')
        phone = request.form.get('phone')
        vh_type = request.form.get('r')
        vh_no = request.form.get('vhnum')
        pickup = request.form.get('pd')
        new_driver = Driver(name=name, phone=phone, vh_type=vh_type,vh_no=vh_no, pickup=pickup)
        db.session.add(new_driver)
        db.session.commit()
        flash(f"You have successfully created a ride!!!",category="ctride_msg")
        return redirect(url_for('ctride'))
    elif request.method == 'GET':
        return render_template('ctride.html')

@app.route('/rides')
def rides():
    pickup = session.get('pickup')
    print(f"Pickup Location: {[pickup]}")
    # Query available drivers with the same pickup location
    if pickup:
        available_drivers = Driver.query.filter_by(pickup=pickup, avail=True).order_by(Driver.pickup.asc()).all()

        if available_drivers:
            return render_template('rides.html', available_drivers=available_drivers)
        else:
            flash("No available rides for the selected pickup location.")
            return redirect(url_for('index'))
    
    flash("No pickup location selected.")
    return redirect(url_for('index'))
     
@app.route('/book/<int:driver_id>', methods=['POST'])
def book_ride(driver_id):
    driver = Driver.query.get(driver_id)
    pickup = session.get('pickup')  # Get pickup location from session

    if driver:
        # Delete the driver
        db.session.delete(driver)

        # Find and delete the customer with the same pickup (latest one)
        customer = Customer.query.filter_by(pickup=pickup).order_by(Customer.Sno.desc()).first()
        if customer:
            db.session.delete(customer)

        db.session.commit()

        # Set flash message after the operation
        flash(f"You have successfully booked a ride with {driver.name}!")
    else:
        flash("This ride is no longer available.")

    # Clear the session after booking
    session.pop('pickup', None)

    # Redirect the user to the rides page to see the flash message
    return render_template('rides.html')
    
@app.route('/searide',methods=['GET','POST'])
def searide():
     
     print(request.method)
     if request.method == 'POST':
        name = request.form.get('un')
        phone = request.form.get('phone')
        pickup = request.form.get('pd')

        # Save customer
        new_cust = Customer(name=name, phone=phone, pickup=pickup)
        db.session.add(new_cust)
        db.session.commit()

        # Store pickup in session
        session['pickup'] = pickup
        print(f"Pickup Location set in session: {session['pickup']}")

        # Query for available drivers at the pickup location
        available_drivers = Driver.query.filter_by(pickup=pickup, avail=True).all()

        return render_template('rides.html', available_drivers=available_drivers)
    
     return render_template('searide.html')
     
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)