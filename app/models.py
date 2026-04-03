from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('PracticeSubmission', backref='user', lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False, index=True)
    province = db.Column(db.String(100), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    grade = db.Column(db.String(20), nullable=False, index=True)
    knowledge_point = db.Column(db.String(255), nullable=False)
    requirement = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    examples = db.relationship('ExampleQuestion', backref='topic', lazy=True, cascade='all, delete-orphan')
    exercises = db.relationship('ExerciseQuestion', backref='topic', lazy=True, cascade='all, delete-orphan')


class ExampleQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    question = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    exam_tips = db.Column(db.Text, nullable=False)
    country_version = db.Column(db.String(100), nullable=True)


class ExerciseQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    question = db.Column(db.Text, nullable=False)
    standard_answer = db.Column(db.Text, nullable=False)
    marking_points = db.Column(db.Text, nullable=False)


class PracticeSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise_question.id'), nullable=False)
    uploaded_answer_text = db.Column(db.Text, nullable=True)
    uploaded_file_path = db.Column(db.String(255), nullable=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    standard_answer_snapshot = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercise = db.relationship('ExerciseQuestion')
