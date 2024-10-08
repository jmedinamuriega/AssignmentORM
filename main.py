from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Gringochone0@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    members = db.relationship('Member', backref='trainer', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='member', lazy=True)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    duration = db.Column(db.Integer)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)


with app.app_context():
    db.create_all()

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    trainer = Trainer.query.get(data['trainer_id'])
    if not trainer:
        return jsonify({'error': 'Trainer not found'}), 404
    
    new_member = Member(name=data['name'], age=data['age'], trainer_id=data['trainer_id'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added successfully'}), 201


@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify({
        'id': member.id,
        'name': member.name,
        'age': member.age,
        'trainer_id': member.trainer_id,
        'trainer_name': member.trainer.name
    })


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
    member = Member.query.get(data['member_id'])
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    new_session = WorkoutSession(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        duration=data['duration'],
        member_id=data['member_id']
    )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'}), 201


@app.route('/workout_sessions/<int:member_id>', methods=['GET'])
def get_workout_sessions(member_id):
    member = Member.query.get_or_404(member_id)
    session_list = [{
        'id': session.id,
        'date': session.date.isoformat(),
        'duration': session.duration,
        'member_id': session.member_id
    } for session in member.workout_sessions]
    return jsonify({'workout_sessions': session_list})


@app.route('/trainers/<int:trainer_id>/members', methods=['GET'])
def get_trainer_members(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    member_list = [{
        'id': member.id,
        'name': member.name,
        'age': member.age
    } for member in trainer.members]
    return jsonify({'members': member_list})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


if __name__ == '__main__':
    app.run(debug=True)
