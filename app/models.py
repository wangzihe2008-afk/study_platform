from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CurriculumUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(200), nullable=False)
    requirements_json = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    resources_json = db.Column(db.Text, nullable=True)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(200), nullable=False)
    question_type = db.Column(db.String(30), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    question = db.Column(db.Text, nullable=False)
    choice_a = db.Column(db.Text)
    choice_b = db.Column(db.Text)
    choice_c = db.Column(db.Text)
    choice_d = db.Column(db.Text)
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    marking_points = db.Column(db.Text, nullable=True)
    score_value = db.Column(db.Float, nullable=False, default=1.0)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(200), nullable=False)
    question_type = db.Column(db.String(30), nullable=False)
    question_snapshot = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    correct_answer_snapshot = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    max_score = db.Column(db.Float, nullable=False, default=1.0)
    explanation_snapshot = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
