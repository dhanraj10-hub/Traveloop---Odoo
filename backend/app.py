from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'traveloop_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traveloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── MODELS ────────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), default='')
    language = db.Column(db.String(20), default='English')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    cover_photo = db.Column(db.String(200), default='')
    is_public = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stops = db.relationship('Stop', backref='trip', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='trip', lazy=True, cascade='all, delete-orphan')
    checklist = db.relationship('ChecklistItem', backref='trip', lazy=True, cascade='all, delete-orphan')

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='')
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, default=0)
    activities = db.relationship('Activity', backref='stop', lazy=True, cascade='all, delete-orphan')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='sightseeing')
    cost = db.Column(db.Float, default=0.0)
    duration = db.Column(db.String(50), default='')
    description = db.Column(db.Text, default='')
    time_slot = db.Column(db.String(50), default='')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    stop_ref = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    item = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='general')
    is_packed = db.Column(db.Boolean, default=False)

# ─── ROUTES ────────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.created_at.desc()).limit(6).all()
    return render_template('dashboard.html', user=user, trips=trips)

@app.route('/trips')
@login_required
def my_trips():
    user = User.query.get(session['user_id'])
    trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.created_at.desc()).all()
    return render_template('my_trips.html', user=user, trips=trips)

@app.route('/trips/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        trip = Trip(
            user_id=session['user_id'],
            name=request.form.get('name'),
            description=request.form.get('description', ''),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date'),
            budget=float(request.form.get('budget', 0)),
            is_public=bool(request.form.get('is_public'))
        )
        db.session.add(trip)
        db.session.commit()
        return redirect(url_for('itinerary_builder', trip_id=trip.id))
    return render_template('create_trip.html', user=User.query.get(session['user_id']))

@app.route('/trips/<int:trip_id>/builder', methods=['GET', 'POST'])
@login_required
def itinerary_builder(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        stop = Stop(
            trip_id=trip_id,
            city=request.form.get('city'),
            country=request.form.get('country', ''),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date'),
            order=len(trip.stops)
        )
        db.session.add(stop)
        db.session.commit()
        return redirect(url_for('itinerary_builder', trip_id=trip_id))
    return render_template('itinerary_builder.html', trip=trip, user=User.query.get(session['user_id']))

@app.route('/trips/<int:trip_id>/view')
def itinerary_view(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if not trip.is_public and ('user_id' not in session or trip.user_id != session['user_id']):
        return redirect(url_for('login'))
    owner = User.query.get(trip.user_id)
    total_cost = sum(a.cost for s in trip.stops for a in s.activities)
    return render_template('itinerary_view.html', trip=trip, owner=owner, total_cost=total_cost,
                           user=User.query.get(session['user_id']) if 'user_id' in session else None)

@app.route('/trips/<int:trip_id>/budget')
@login_required
def trip_budget(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    categories = {}
    for stop in trip.stops:
        for act in stop.activities:
            categories[act.category] = categories.get(act.category, 0) + act.cost
    total = sum(categories.values())
    return render_template('budget.html', trip=trip, categories=categories, total=total,
                           user=User.query.get(session['user_id']))

@app.route('/trips/<int:trip_id>/checklist', methods=['GET', 'POST'])
@login_required
def checklist(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        item = ChecklistItem(
            trip_id=trip_id,
            item=request.form.get('item'),
            category=request.form.get('category', 'general')
        )
        db.session.add(item)
        db.session.commit()
    return render_template('checklist.html', trip=trip, user=User.query.get(session['user_id']))

@app.route('/trips/<int:trip_id>/notes', methods=['GET', 'POST'])
@login_required
def trip_notes(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        note = Note(trip_id=trip_id, content=request.form.get('content'),
                    stop_ref=request.form.get('stop_ref', ''))
        db.session.add(note)
        db.session.commit()
    return render_template('notes.html', trip=trip, user=User.query.get(session['user_id']))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.language = request.form.get('language', user.language)
        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated!', 'success')
    return render_template('profile.html', user=user)

# ─── API ENDPOINTS ─────────────────────────────────────────────────────────────

@app.route('/api/stops/<int:stop_id>/activities', methods=['POST'])
@login_required
def add_activity(stop_id):
    data = request.json
    activity = Activity(
        stop_id=stop_id,
        name=data.get('name'),
        category=data.get('category', 'sightseeing'),
        cost=float(data.get('cost', 0)),
        duration=data.get('duration', ''),
        description=data.get('description', ''),
        time_slot=data.get('time_slot', '')
    )
    db.session.add(activity)
    db.session.commit()
    return jsonify({'success': True, 'id': activity.id})

@app.route('/api/activities/<int:act_id>', methods=['DELETE'])
@login_required
def delete_activity(act_id):
    act = Activity.query.get_or_404(act_id)
    db.session.delete(act)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stops/<int:stop_id>', methods=['DELETE'])
@login_required
def delete_stop(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    db.session.delete(stop)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/checklist/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_checklist(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    item.is_packed = not item.is_packed
    db.session.commit()
    return jsonify({'success': True, 'is_packed': item.is_packed})

@app.route('/api/checklist/<int:item_id>', methods=['DELETE'])
@login_required
def delete_checklist(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/trips/<int:trip_id>/toggle_public', methods=['POST'])
@login_required
def toggle_public(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id == session['user_id']:
        trip.is_public = not trip.is_public
        db.session.commit()
    return jsonify({'success': True, 'is_public': trip.is_public})

@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id == session['user_id']:
        db.session.delete(trip)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/cities/search')
def search_cities():
    q = request.args.get('q', '').lower()
    cities = [
        {"name": "Paris", "country": "France", "cost_index": "High", "popularity": 98},
        {"name": "Tokyo", "country": "Japan", "cost_index": "Medium", "popularity": 96},
        {"name": "New York", "country": "USA", "cost_index": "High", "popularity": 95},
        {"name": "Bali", "country": "Indonesia", "cost_index": "Low", "popularity": 94},
        {"name": "London", "country": "UK", "cost_index": "High", "popularity": 93},
        {"name": "Bangkok", "country": "Thailand", "cost_index": "Low", "popularity": 92},
        {"name": "Dubai", "country": "UAE", "cost_index": "High", "popularity": 91},
        {"name": "Rome", "country": "Italy", "cost_index": "Medium", "popularity": 90},
        {"name": "Barcelona", "country": "Spain", "cost_index": "Medium", "popularity": 89},
        {"name": "Amsterdam", "country": "Netherlands", "cost_index": "Medium", "popularity": 88},
        {"name": "Sydney", "country": "Australia", "cost_index": "High", "popularity": 87},
        {"name": "Singapore", "country": "Singapore", "cost_index": "High", "popularity": 86},
        {"name": "Prague", "country": "Czech Republic", "cost_index": "Low", "popularity": 85},
        {"name": "Istanbul", "country": "Turkey", "cost_index": "Low", "popularity": 84},
        {"name": "Lisbon", "country": "Portugal", "cost_index": "Medium", "popularity": 83},
        {"name": "Mumbai", "country": "India", "cost_index": "Low", "popularity": 82},
        {"name": "Goa", "country": "India", "cost_index": "Low", "popularity": 80},
        {"name": "Kyoto", "country": "Japan", "cost_index": "Medium", "popularity": 88},
        {"name": "Santorini", "country": "Greece", "cost_index": "High", "popularity": 91},
        {"name": "Maldives", "country": "Maldives", "cost_index": "Very High", "popularity": 93},
    ]
    filtered = [c for c in cities if q in c['name'].lower() or q in c['country'].lower()] if q else cities
    return jsonify(filtered)

@app.route('/api/activities/search')
def search_activities():
    q = request.args.get('q', '').lower()
    cat = request.args.get('category', '')
    activities = [
        {"name": "Eiffel Tower Visit", "category": "sightseeing", "cost": 25, "duration": "2-3 hrs", "description": "Iconic iron lattice tower in Paris"},
        {"name": "Sushi Making Class", "category": "food", "cost": 80, "duration": "3 hrs", "description": "Learn to make authentic Japanese sushi"},
        {"name": "River Seine Cruise", "category": "adventure", "cost": 15, "duration": "1 hr", "description": "Scenic boat tour along Seine river"},
        {"name": "Colosseum Tour", "category": "sightseeing", "cost": 20, "duration": "2 hrs", "description": "Ancient Roman amphitheater guided tour"},
        {"name": "Surfing Lesson", "category": "adventure", "cost": 50, "duration": "2 hrs", "description": "Learn surfing on Bali beaches"},
        {"name": "Street Food Tour", "category": "food", "cost": 30, "duration": "3 hrs", "description": "Explore local street food culture"},
        {"name": "Spa & Wellness", "category": "wellness", "cost": 60, "duration": "2 hrs", "description": "Traditional massage and wellness"},
        {"name": "Museum Visit", "category": "culture", "cost": 15, "duration": "3 hrs", "description": "Explore local art and history"},
        {"name": "Hiking Trek", "category": "adventure", "cost": 25, "duration": "Full day", "description": "Mountain or nature trek experience"},
        {"name": "Sunset Cruise", "category": "sightseeing", "cost": 45, "duration": "2 hrs", "description": "Evening cruise with sunset views"},
        {"name": "Cooking Class", "category": "food", "cost": 70, "duration": "4 hrs", "description": "Learn authentic local cuisine"},
        {"name": "City Walking Tour", "category": "culture", "cost": 20, "duration": "3 hrs", "description": "Guided walk through historic city center"},
    ]
    filtered = activities
    if q:
        filtered = [a for a in filtered if q in a['name'].lower() or q in a['description'].lower()]
    if cat:
        filtered = [a for a in filtered if a['category'] == cat]
    return jsonify(filtered)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
    
import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)