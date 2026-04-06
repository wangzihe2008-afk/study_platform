import json, random, os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, CurriculumUnit, QuizQuestion, QuizAttempt
from .photo_ocr import analyze_question_page

main = Blueprint("main", __name__)

def parse_json(text, default):
    try:
        return json.loads(text) if text else default
    except Exception:
        return default

def score_written(user_answer: str, correct_answer: str, marking_points: str, max_score: float):
    if not user_answer or not user_answer.strip():
        return 0.0, "未作答。"
    answer = user_answer.lower()
    keywords = [x.strip().lower() for x in marking_points.split(",") if x.strip()]
    matched = [kw for kw in keywords if kw in answer]
    ratio = len(matched) / max(1, len(keywords)) if keywords else 0.5
    score = round(max_score * max(0.3, ratio), 1)
    feedback = f"匹配到的关键词：{', '.join(matched) if matched else '无'}\n评分参考点：{marking_points}"
    return score, feedback

def _queue_key(country, province, grade, subject, qtype):
    return f"quiz_queue::{country}::{province}::{grade}::{subject}::{qtype}"

def build_queue(country, province, grade, subject, qtype, preferred_unit=None):
    items = QuizQuestion.query.filter_by(
        country=country, province=province, grade=grade, subject=subject, question_type=qtype
    ).all()
    if not items:
        return []
    preferred = [q.id for q in items if preferred_unit and q.unit == preferred_unit]
    others = [q.id for q in items if q.id not in preferred]
    random.shuffle(preferred)
    random.shuffle(others)
    return preferred + others

@main.route("/")
def home():
    return redirect(url_for("main.dashboard")) if current_user.is_authenticated else redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        last_name = request.form.get("last_name", "").strip()
        first_name = request.form.get("first_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        if not all([last_name, first_name, email, password]):
            flash("请完整填写所有注册信息。", "danger")
            return redirect(url_for("main.register"))
        if User.query.filter_by(email=email).first():
            flash("该邮箱已经注册。", "danger")
            return redirect(url_for("main.register"))
        user = User(last_name=last_name, first_name=first_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("注册成功，请登录。", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("邮箱或密码错误。", "danger")
    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已退出登录。", "success")
    return redirect(url_for("main.login"))

@main.route("/dashboard")
@login_required
def dashboard():
    countries = sorted({u.country for u in CurriculumUnit.query.all()})
    return render_template("dashboard.html", countries=countries, user=current_user)

@main.route("/api/provinces")
@login_required
def api_provinces():
    country = request.args.get("country", "")
    data = sorted({u.province for u in CurriculumUnit.query.filter_by(country=country).all()})
    return jsonify(data)

@main.route("/api/grades")
@login_required
def api_grades():
    country = request.args.get("country", "")
    province = request.args.get("province", "")
    data = sorted({u.grade for u in CurriculumUnit.query.filter_by(country=country, province=province).all()}, key=lambda x: int(x))
    return jsonify(data)

@main.route("/api/subjects")
@login_required
def api_subjects():
    country = request.args.get("country", "")
    province = request.args.get("province", "")
    grade = request.args.get("grade", "")
    data = sorted({u.subject for u in CurriculumUnit.query.filter_by(country=country, province=province, grade=grade).all()})
    return jsonify(data)

@main.route("/api/units")
@login_required
def api_units():
    country = request.args.get("country", "")
    province = request.args.get("province", "")
    grade = request.args.get("grade", "")
    subject = request.args.get("subject", "")
    units = CurriculumUnit.query.filter_by(country=country, province=province, grade=grade, subject=subject).order_by(CurriculumUnit.id.asc()).all()
    data = []
    for u in units:
        data.append({
            "id": u.id,
            "unit": u.unit,
            "requirements": parse_json(u.requirements_json, []),
            "content": u.content,
            "resources": parse_json(u.resources_json, [])
        })
    return jsonify(data)

@main.route("/quiz/start", methods=["POST"])
@login_required
def quiz_start():
    country = request.form.get("country", "")
    province = request.form.get("province", "")
    grade = request.form.get("grade", "")
    subject = request.form.get("subject", "")
    preferred_unit = request.form.get("unit", "")
    qtype = request.form.get("question_type", "")
    queue = build_queue(country, province, grade, subject, qtype, preferred_unit=preferred_unit)
    if not queue:
        flash("没有找到对应题目。", "danger")
        return redirect(url_for("main.dashboard"))
    session[_queue_key(country, province, grade, subject, qtype)] = queue
    return redirect(url_for("main.quiz_next", country=country, province=province, grade=grade, subject=subject, qtype=qtype))

@main.route("/quiz/next")
@login_required
def quiz_next():
    country = request.args.get("country", "")
    province = request.args.get("province", "")
    grade = request.args.get("grade", "")
    subject = request.args.get("subject", "")
    qtype = request.args.get("qtype", "")
    key = _queue_key(country, province, grade, subject, qtype)
    queue = session.get(key, [])
    if not queue:
        queue = build_queue(country, province, grade, subject, qtype)
    if not queue:
        flash("这个筛选条件下没有题目。", "danger")
        return redirect(url_for("main.dashboard"))
    qid = queue.pop(0)
    session[key] = queue
    session.modified = True
    q = db.session.get(QuizQuestion, qid)
    return render_template("quiz_one.html", q=q, filter_info={
        "country": country, "province": province, "grade": grade, "subject": subject, "question_type": qtype
    })

@main.route("/quiz/submit_one", methods=["POST"])
@login_required
def quiz_submit_one():
    qid = int(request.form.get("qid"))
    q = db.session.get(QuizQuestion, qid)
    user_answer = request.form.get("answer", "").strip()
    country = request.form.get("country", "")
    province = request.form.get("province", "")
    grade = request.form.get("grade", "")
    subject = request.form.get("subject", "")
    qtype = request.form.get("question_type", "")
    feedback_extra = ""
    if q.question_type in ("multiple_choice", "true_false"):
        is_correct = user_answer == q.correct_answer
        score = q.score_value if is_correct else 0.0
    else:
        score, feedback_extra = score_written(user_answer, q.correct_answer, q.marking_points or "", q.score_value)
        is_correct = score >= q.score_value * 0.6

    db.session.add(QuizAttempt(
        user_id=current_user.id, country=q.country, province=q.province, grade=q.grade, subject=q.subject,
        unit=q.unit, question_type=q.question_type, question_snapshot=q.question, user_answer=user_answer,
        correct_answer_snapshot=q.correct_answer, is_correct=is_correct, score=score, max_score=q.score_value,
        explanation_snapshot=q.explanation + ("\n\n" + feedback_extra if feedback_extra else "")
    ))
    db.session.commit()

    return render_template("quiz_result_one.html", q=q, user_answer=user_answer or "未作答", is_correct=is_correct,
                           score=score, max_score=q.score_value, feedback_extra=feedback_extra,
                           next_info={"country": country, "province": province, "grade": grade, "subject": subject, "qtype": qtype})

@main.route("/photo-upload")
@login_required
def photo_upload():
    countries = sorted({u.country for u in CurriculumUnit.query.all()})
    return render_template("photo_upload.html", countries=countries)

@main.route("/photo-analyze", methods=["POST"])
@login_required
def photo_analyze():
    country = request.form.get("country", "")
    province = request.form.get("province", "")
    grade = request.form.get("grade", "")
    subject = request.form.get("subject", "")
    image = request.files.get("photo")
    if not image or not image.filename:
        flash("请先上传图片。", "danger")
        return redirect(url_for("main.photo_upload"))
    ext = os.path.splitext(image.filename)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        flash("只支持 png / jpg / jpeg / webp 图片。", "danger")
        return redirect(url_for("main.photo_upload"))

    upload_dir = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    save_name = f"user_{current_user.id}_{image.filename}"
    save_path = os.path.join(upload_dir, save_name)
    image.save(save_path)

    try:
        data = analyze_question_page(save_path, subject or "")
        questions = data.get("questions", [])
        if not questions:
            flash("识别到了图片，但没有成功拆出题目。可以换一张更清晰的图片再试。", "danger")
            return redirect(url_for("main.photo_upload"))
        return render_template("photo_results.html", questions=questions, context={
            "country": country, "province": province, "grade": grade, "subject": subject
        })
    except Exception as e:
        flash(f"图片识别失败：{e}", "danger")
        return redirect(url_for("main.photo_upload"))

@main.route("/history")
@login_required
def history():
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.created_at.desc()).all()
    return render_template("history.html", attempts=attempts)
