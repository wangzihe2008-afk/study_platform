import os
import uuid
import html
import random
import requests

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
    session,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import select

from . import db
from .models import User, Topic, ExampleQuestion, ExerciseQuestion, PracticeSubmission
from .seed import seed_data

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def simple_score(user_answer: str, standard_answer: str, marking_points: str):
    if not user_answer:
        return 0, '没有检测到文字答案，当前版本建议至少输入文字答案再评分。'

    expected_keywords = []
    for token in standard_answer.replace(',', ' ').replace('.', ' ').split():
        t = token.strip().lower()
        if len(t) >= 2:
            expected_keywords.append(t)
    expected_keywords = list(dict.fromkeys(expected_keywords))[:8]

    answer_lower = user_answer.lower()
    hits = [kw for kw in expected_keywords if kw in answer_lower]
    ratio = len(hits) / max(1, len(expected_keywords))
    score = round(ratio * 100, 1)

    feedback = []
    feedback.append(f'匹配到的关键点: {", ".join(hits) if hits else "无"}')
    missed = [kw for kw in expected_keywords if kw not in hits]
    if missed:
        feedback.append(f'可能缺少的关键点: {", ".join(missed[:5])}')
    feedback.append(f'参考评分规则: {marking_points}')
    if score >= 85:
        feedback.append('整体完成度较好。')
    elif score >= 60:
        feedback.append('基础步骤有了，但还有部分关键点不完整。')
    else:
        feedback.append('建议补充公式、步骤、单位或最终结论。')

    return score, '\n'.join(feedback)


def fetch_trivia_questions(amount=5, difficulty="", qtype="multiple", category="19"):
    url = "https://opentdb.com/api.php"

    attempts = [
        {"amount": amount, "category": category, "difficulty": difficulty, "type": qtype},
        {"amount": amount, "category": category, "type": qtype},
        {"amount": amount, "category": category},
        {"amount": amount},
    ]

    for params in attempts:
        clean_params = {k: v for k, v in params.items() if v}
        try:
            resp = requests.get(url, params=clean_params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            print("DEBUG params =", clean_params)
            print("DEBUG response_code =", data.get("response_code"))

            if data.get("response_code") == 0 and data.get("results"):
                questions = []
                for item in data["results"]:
                    correct = html.unescape(item["correct_answer"])
                    incorrect = [html.unescape(x) for x in item["incorrect_answers"]]
                    choices = incorrect + [correct]
                    random.shuffle(choices)

                    questions.append({
                        "question": html.unescape(item["question"]),
                        "correct_answer": correct,
                        "choices": choices,
                        "difficulty": item.get("difficulty", ""),
                        "type": item.get("type", ""),
                        "category": item.get("category", "")
                    })
                return questions
        except Exception as e:
            print("DEBUG fetch error =", e)

    return []


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        last_name = request.form.get('last_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not all([last_name, first_name, email, password]):
            flash('请完整填写所有注册信息。', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('该邮箱已经注册。', 'danger')
            return redirect(url_for('main.register'))

        user = User(last_name=last_name, first_name=first_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录。', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            seed_data()
            return redirect(url_for('main.dashboard'))
        flash('邮箱或密码错误。', 'danger')
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录。', 'success')
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    seed_data()
    countries = db.session.execute(select(Topic.country).distinct()).scalars().all()
    provinces = db.session.execute(select(Topic.province).distinct()).scalars().all()
    grades = db.session.execute(select(Topic.grade).distinct()).scalars().all()
    return render_template('dashboard.html', countries=countries, provinces=provinces, grades=grades)


@main.route('/api/topics')
@login_required
def api_topics():
    country = request.args.get('country')
    province = request.args.get('province')
    subject = request.args.get('subject')
    grade = request.args.get('grade')

    query = Topic.query
    if country:
        query = query.filter_by(country=country)
    if province:
        query = query.filter_by(province=province)
    if subject:
        query = query.filter_by(subject=subject)
    if grade:
        query = query.filter_by(grade=grade)

    topics = query.all()
    return jsonify([
        {
            'id': t.id,
            'knowledge_point': t.knowledge_point,
            'requirement': t.requirement,
            'explanation': t.explanation,
        }
        for t in topics
    ])


@main.route('/api/topic/<int:topic_id>/examples')
@login_required
def api_examples(topic_id):
    difficulty = request.args.get('difficulty')
    query = ExampleQuestion.query.filter_by(topic_id=topic_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    items = query.all()
    return jsonify([
        {
            'id': i.id,
            'title': i.title,
            'difficulty': i.difficulty,
            'question': i.question,
        }
        for i in items
    ])


@main.route('/api/example/<int:example_id>')
@login_required
def api_example_detail(example_id):
    item = db.session.get(ExampleQuestion, example_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'id': item.id,
        'title': item.title,
        'difficulty': item.difficulty,
        'question': item.question,
        'solution': item.solution,
        'exam_tips': item.exam_tips,
        'country_version': item.country_version,
    })


@main.route('/api/example/<int:example_id>/compare')
@login_required
def api_example_compare(example_id):
    country = request.args.get('country', 'Canada')
    item = db.session.get(ExampleQuestion, example_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404

    compared_solution = f'[{country} 标准] ' + item.solution
    compared_tips = f'[{country} 要点说明] ' + item.exam_tips
    return jsonify({
        'title': item.title,
        'country': country,
        'solution': compared_solution,
        'exam_tips': compared_tips,
    })


@main.route('/api/topic/<int:topic_id>/exercises')
@login_required
def api_exercises(topic_id):
    difficulty = request.args.get('difficulty')
    limit = request.args.get('limit', type=int)

    query = ExerciseQuestion.query.filter_by(topic_id=topic_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    items = query.all()
    if limit:
        items = items[:limit]
    return jsonify([
        {
            'id': i.id,
            'title': i.title,
            'difficulty': i.difficulty,
            'question': i.question,
        }
        for i in items
    ])


@main.route('/api/exercise/<int:exercise_id>')
@login_required
def api_exercise_detail(exercise_id):
    item = db.session.get(ExerciseQuestion, exercise_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'id': item.id,
        'title': item.title,
        'difficulty': item.difficulty,
        'question': item.question,
    })


@main.route('/api/exercise/<int:exercise_id>/standard-answer')
@login_required
def api_standard_answer(exercise_id):
    item = db.session.get(ExerciseQuestion, exercise_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'standard_answer': item.standard_answer,
        'marking_points': item.marking_points,
    })


@main.route('/api/exercise/<int:exercise_id>/submit', methods=['POST'])
@login_required
def api_submit_exercise(exercise_id):
    item = db.session.get(ExerciseQuestion, exercise_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404

    answer_text = request.form.get('answer_text', '').strip()
    file = request.files.get('answer_file')
    file_path = None

    if file and file.filename:
        if allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'{uuid.uuid4().hex}.{ext}'
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
            file.save(save_path)
            file_path = save_path
        else:
            return jsonify({'error': '文件类型不支持'}), 400

    score, feedback = simple_score(answer_text, item.standard_answer, item.marking_points)

    submission = PracticeSubmission(
        user_id=current_user.id,
        exercise_id=item.id,
        uploaded_answer_text=answer_text or None,
        uploaded_file_path=file_path,
        score=score,
        feedback=feedback,
        standard_answer_snapshot=item.standard_answer,
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'submission_id': submission.id,
        'score': score,
        'feedback': feedback,
        'standard_answer': item.standard_answer,
    })


@main.route('/submissions')
@login_required
def submissions():
    items = PracticeSubmission.query.filter_by(user_id=current_user.id).order_by(PracticeSubmission.created_at.desc()).all()
    return render_template('submissions.html', submissions=items)


@main.route('/trivia', methods=['GET', 'POST'])
@login_required
def trivia():
    if request.method == 'POST':
        amount = int(request.form.get('amount', 5))
        difficulty = request.form.get('difficulty', '')
        qtype = request.form.get('qtype', 'multiple')

        questions = fetch_trivia_questions(
            amount=amount,
            difficulty=difficulty,
            qtype=qtype,
            category='19'
        )

        if not questions:
            flash('没有拿到题目，请换个难度或题型再试。', 'danger')
            return redirect(url_for('main.trivia'))

        session['trivia_questions'] = questions
        print("DEBUG len(questions) =", len(questions))
        return render_template('trivia_quiz.html', questions=questions)

    return render_template('trivia_form.html')



@main.route('/trivia/submit', methods=['POST'])
@login_required
def trivia_submit():
    questions = session.get('trivia_questions', [])
    if not questions:
        flash('题目已失效，请重新开始。', 'danger')
        return redirect(url_for('main.trivia'))

    score = 0
    results = []

    for i, q in enumerate(questions):
        user_answer = request.form.get(f'q{i}', '')
        is_correct = user_answer == q['correct_answer']

        if is_correct:
            score += 1

        results.append({
            'question': q['question'],
            'choices': q['choices'],
            'correct_answer': q['correct_answer'],
            'user_answer': user_answer,
            'is_correct': is_correct
        })

    percent = round(score / len(questions) * 100, 1) if questions else 0

    return render_template(
        'trivia_result.html',
        results=results,
        score=score,
        total=len(questions),
        percent=percent
    )