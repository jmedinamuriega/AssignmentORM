from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Gringochone0@localhost/fitness_center_db'
db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    duration = db.Column(db.Integer)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], age=data['age'], trainer_id=data['trainer_id'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added successfully'})

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify({'id': member.id, 'name': member.name, 'age': member.age, 'trainer_id': member.trainer_id})

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data['name']
    member.age = data['age']
    member.trainer_id = data['trainer_id']
    db.session.commit()
    return jsonify({'message': 'Member updated successfully'})

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})



@app.route('/workout_sessions', methods=['POST'])
def schedule_workout_session():
    data = request.get_json()
    new_session = WorkoutSession(date=data['date'], duration=data['duration'], member_id=data['member_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'})

@app.route('/workout_sessions/<int:member_id>', methods=['GET'])
def get_workout_sessions(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    session_list = []
    for session in sessions:
        session_list.append({'id': session.id, 'date': session.date, 'duration': session.duration, 'member_id': session.member_id})
    return jsonify({'workout_sessions': session_list})

if __name__ == '__main__':
    app.run(debug=True)
