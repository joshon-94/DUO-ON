"""듀온 - 가치관/취향 기반 소개팅 플랫폼

로컬 실행:   python app.py   -> http://127.0.0.1:5000
배포(Render): gunicorn app:app  (DATABASE_URL 환경변수로 PostgreSQL 사용)
"""
import datetime
import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Like
from questions import (
    QUESTIONS, match_score, option_label, shared_highlights
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "duon-dev-secret-change-me")

# DB 연결: 배포 시 DATABASE_URL(PostgreSQL), 없으면 로컬 SQLite
db_url = os.environ.get("DATABASE_URL", "sqlite:///duon.db")
if db_url.startswith("postgres://"):  # Render 구형 URL 보정
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

CURRENT_YEAR = datetime.date.today().year

# 관리자 계정 정보 (배포 시 환경변수로 지정)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@duon.com").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")


def ensure_admin():
    """관리자 계정이 없으면 생성."""
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            name="관리자", gender="M", birth_year=1990,
            is_admin=True, onboarded=False,
        )
        db.session.add(admin)
        db.session.commit()
    elif not admin.is_admin:
        admin.is_admin = True
        db.session.commit()


def ensure_seed():
    """일반 회원이 한 명도 없으면 샘플 데이터를 넣어 빈 사이트 방지."""
    if User.query.filter_by(is_admin=False).count() == 0:
        try:
            import seed
            seed.run()
        except Exception as exc:  # 시드 실패해도 앱은 떠야 함
            print("seed skipped:", exc)


with app.app_context():
    db.create_all()
    ensure_admin()
    ensure_seed()


# ---------- 유틸 ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or not user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def photo_for(user):
    """사진 URL 반환: photo_url 우선, 없으면 None(템플릿에서 그라데이션 처리)."""
    if user is None:
        return None
    return user.photo_url or None


@app.context_processor
def inject_globals():
    return {"me": current_user(), "current_year": CURRENT_YEAR,
            "photo_for": photo_for}


@app.template_filter("age")
def age_filter(birth_year):
    if not birth_year:
        return ""
    return CURRENT_YEAR - int(birth_year) + 1  # 한국 나이 느낌


def collect_answers_from_form(form):
    """온보딩/관리자 폼에서 설문 답변 dict를 만든다."""
    answers = {}
    for q in QUESTIONS:
        if q["type"] == "multi":
            value = ",".join(form.getlist(q["id"]))
        else:
            value = form.get(q["id"], "")
        if value:
            answers[q["id"]] = value
    return answers


def group_answers(answers, my_answers=None):
    """답변을 카테고리(values/taste)별 라벨 리스트로 정리."""
    grouped = {"values": [], "taste": []}
    for q in QUESTIONS:
        val = answers.get(q["id"])
        if not val:
            continue
        if q["type"] == "multi":
            display = ", ".join(option_label(q["id"], k) for k in val.split(",") if k)
        else:
            display = option_label(q["id"], val)
        same = False
        if my_answers and q["type"] != "multi":
            same = my_answers.get(q["id"]) == val
        grouped[q["category"]].append(
            {"text": q["text"], "display": display, "same": same}
        )
    return grouped


# ---------- 일반 라우트 ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        email = f.get("email", "").strip().lower()
        password = f.get("password", "")
        name = f.get("name", "").strip()
        gender = f.get("gender")
        birth_year = f.get("birth_year")
        location = f.get("location", "").strip()

        if not (email and password and name and gender and birth_year):
            flash("필수 항목을 모두 입력해 주세요.", "error")
            return render_template("register.html", form=f)

        if User.query.filter_by(email=email).first():
            flash("이미 가입된 이메일이에요.", "error")
            return render_template("register.html", form=f)

        user = User(
            email=email, password_hash=generate_password_hash(password),
            name=name, gender=gender, birth_year=int(birth_year),
            location=location,
        )
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        flash("환영해요! 가치관·취향 설문을 완성하면 추천이 시작돼요.", "success")
        return redirect(url_for("onboarding"))

    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            if user.is_admin:
                return redirect(url_for("admin_list"))
            return redirect(url_for("home"))
        flash("이메일 또는 비밀번호가 올바르지 않아요.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    user = current_user()
    if request.method == "POST":
        user.set_answers(collect_answers_from_form(request.form))
        user.onboarded = True
        db.session.commit()
        flash("설문이 저장됐어요. 맞는 상대를 찾아볼까요?", "success")
        return redirect(url_for("home"))
    return render_template(
        "onboarding.html", questions=QUESTIONS, answers=user.get_answers()
    )


@app.route("/home")
@login_required
def home():
    me = current_user()
    if me.is_admin:
        return redirect(url_for("admin_list"))
    if not me.onboarded:
        flash("먼저 가치관·취향 설문을 완성해 주세요.", "info")
        return redirect(url_for("onboarding"))

    my_answers = me.get_answers()
    liked = {l.to_user for l in Like.query.filter_by(from_user=me.id).all()}
    target_gender = "F" if me.gender == "M" else "M"
    candidates = User.query.filter(
        User.id != me.id, User.onboarded.is_(True),
        User.gender == target_gender, User.is_admin.is_(False),
    ).all()

    results = []
    for c in candidates:
        if c.id in liked:
            continue
        c_answers = c.get_answers()
        results.append({
            "user": c,
            "match": match_score(my_answers, c_answers),
            "shared": shared_highlights(my_answers, c_answers),
        })
    results.sort(key=lambda r: r["match"]["score"], reverse=True)
    return render_template("home.html", results=results)


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    me = current_user()
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    my_answers = me.get_answers()
    their_answers = user.get_answers()
    score = match_score(my_answers, their_answers)
    grouped = group_answers(their_answers, my_answers)

    already_liked = Like.query.filter_by(
        from_user=me.id, to_user=user_id).first() is not None
    likes_me = Like.query.filter_by(
        from_user=user_id, to_user=me.id).first() is not None

    return render_template(
        "profile.html", user=user, match=score, grouped=grouped,
        already_liked=already_liked, is_match=already_liked and likes_me,
        likes_me=likes_me,
    )


@app.route("/like/<int:user_id>", methods=["POST"])
@login_required
def like(user_id):
    me = current_user()
    if user_id == me.id:
        abort(400)
    if not Like.query.filter_by(from_user=me.id, to_user=user_id).first():
        db.session.add(Like(from_user=me.id, to_user=user_id))
        db.session.commit()
    mutual = Like.query.filter_by(from_user=user_id, to_user=me.id).first() is not None
    flash("서로 좋아요! 매칭이 성사됐어요 💛" if mutual else "좋아요를 보냈어요.", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/matches")
@login_required
def matches():
    me = current_user()
    my_answers = me.get_answers()
    sent = {l.to_user for l in Like.query.filter_by(from_user=me.id).all()}
    got = {l.from_user for l in Like.query.filter_by(to_user=me.id).all()}
    mutual_ids = sent & got
    results = []
    for uid in mutual_ids:
        u = db.session.get(User, uid)
        if not u:
            continue
        u_answers = u.get_answers()
        results.append({
            "user": u,
            "match": match_score(my_answers, u_answers),
            "shared": shared_highlights(my_answers, u_answers),
        })
    results.sort(key=lambda r: r["match"]["score"], reverse=True)
    return render_template("matches.html", results=results)


@app.route("/me", methods=["GET", "POST"])
@login_required
def me_page():
    me = current_user()
    if request.method == "POST":
        me.bio = request.form.get("bio", "").strip()
        me.location = request.form.get("location", "").strip()
        db.session.commit()
        flash("프로필이 저장됐어요.", "success")
        return redirect(url_for("me_page"))
    grouped = group_answers(me.get_answers())
    return render_template("me.html", grouped=grouped)


# ---------- 관리자 라우트 ----------
@app.route("/admin")
@admin_required
def admin_list():
    users = User.query.filter_by(is_admin=False).order_by(User.id.desc()).all()
    return render_template("admin_list.html", users=users)


@app.route("/admin/new", methods=["GET", "POST"])
@admin_required
def admin_new():
    if request.method == "POST":
        result = _save_member(None, request.form)
        if result is True:
            flash("회원이 추가됐어요.", "success")
            return redirect(url_for("admin_list"))
        # 오류 메시지 + 입력값 유지
        return render_template(
            "admin_form.html", questions=QUESTIONS, answers=collect_answers_from_form(request.form),
            user=None, form=request.form, mode="new",
        )
    return render_template(
        "admin_form.html", questions=QUESTIONS, answers={}, user=None,
        form={}, mode="new",
    )


@app.route("/admin/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit(user_id):
    user = db.session.get(User, user_id)
    if not user or user.is_admin:
        abort(404)
    if request.method == "POST":
        result = _save_member(user, request.form)
        if result is True:
            flash("회원 정보가 수정됐어요.", "success")
            return redirect(url_for("admin_list"))
        return render_template(
            "admin_form.html", questions=QUESTIONS,
            answers=collect_answers_from_form(request.form),
            user=user, form=request.form, mode="edit",
        )
    return render_template(
        "admin_form.html", questions=QUESTIONS, answers=user.get_answers(),
        user=user, form=_user_to_form(user), mode="edit",
    )


@app.route("/admin/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete(user_id):
    user = db.session.get(User, user_id)
    if user and not user.is_admin:
        # 관련 좋아요도 정리
        Like.query.filter(
            (Like.from_user == user_id) | (Like.to_user == user_id)
        ).delete(synchronize_session=False)
        db.session.delete(user)
        db.session.commit()
        flash("회원이 삭제됐어요.", "success")
    return redirect(url_for("admin_list"))


def _user_to_form(user):
    return {
        "email": user.email, "name": user.name, "gender": user.gender,
        "birth_year": user.birth_year, "location": user.location or "",
        "bio": user.bio or "", "photo_url": user.photo_url or "",
    }


def _save_member(user, form):
    """관리자 폼으로 회원 생성/수정. 성공 시 True, 실패 시 False(플래시 설정)."""
    email = form.get("email", "").strip().lower()
    name = form.get("name", "").strip()
    gender = form.get("gender")
    birth_year = form.get("birth_year")
    password = form.get("password", "")

    if not (email and name and gender and birth_year):
        flash("이메일·이름·성별·출생연도는 필수예요.", "error")
        return False
    if user is None and not password:
        flash("새 회원은 비밀번호가 필요해요.", "error")
        return False

    # 이메일 중복 검사
    existing = User.query.filter_by(email=email).first()
    if existing and (user is None or existing.id != user.id):
        flash("이미 사용 중인 이메일이에요.", "error")
        return False

    if user is None:
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
    else:
        user.email = email
        if password:  # 입력했을 때만 비밀번호 변경
            user.password_hash = generate_password_hash(password)

    user.name = name
    user.gender = gender
    user.birth_year = int(birth_year)
    user.location = form.get("location", "").strip()
    user.bio = form.get("bio", "").strip()
    user.photo_url = form.get("photo_url", "").strip()
    user.set_answers(collect_answers_from_form(form))
    user.onboarded = True  # 관리자가 넣은 회원은 추천에 바로 노출
    db.session.commit()
    return True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
