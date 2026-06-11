"""듀온 - 가치관/취향 기반 소개팅 플랫폼 (MVP)

실행:
    python app.py
    -> http://127.0.0.1:5000 접속
"""
import datetime
import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db
from questions import (
    QUESTIONS, QUESTION_MAP, match_score, option_label, shared_highlights
)

app = Flask(__name__)
# 배포 환경에서는 SECRET_KEY 환경변수 사용, 없으면 개발용 기본값
app.secret_key = os.environ.get("SECRET_KEY", "duon-dev-secret-change-me")

CURRENT_YEAR = datetime.date.today().year

# gunicorn 등으로 임포트될 때도 DB 테이블이 준비되도록 보장 (idempotent)
init_db()


def _ensure_seed():
    """회원이 한 명도 없으면 샘플 데이터를 넣어 빈 사이트를 방지."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    conn.close()
    if count == 0:
        try:
            import seed
            seed.run()
        except Exception as exc:  # 시드 실패해도 앱은 떠야 함
            print("seed skipped:", exc)


_ensure_seed()


# ---------- 유틸 ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return user


def get_answers(conn, user_id):
    rows = conn.execute(
        "SELECT question_id, value FROM answers WHERE user_id = ?", (user_id,)
    ).fetchall()
    return {r["question_id"]: r["value"] for r in rows}


PHOTO_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def photo_for(user):
    """static/photos 폴더에서 사용자 사진을 찾아 URL 반환(없으면 None).
    파일명 규칙: 이메일 앞부분(예: minji) 또는 사용자 id."""
    photo_dir = os.path.join(app.static_folder, "photos")
    bases = [user["email"].split("@")[0], str(user["id"])]
    for base in bases:
        for ext in PHOTO_EXTS:
            fn = base + ext
            if os.path.exists(os.path.join(photo_dir, fn)):
                return url_for("static", filename="photos/" + fn)
    return None


@app.context_processor
def inject_globals():
    return {"me": current_user(), "current_year": CURRENT_YEAR,
            "photo_for": photo_for}


@app.template_filter("age")
def age_filter(birth_year):
    if not birth_year:
        return ""
    return CURRENT_YEAR - int(birth_year) + 1  # 한국 나이 느낌


# ---------- 라우트 ----------
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

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            conn.close()
            flash("이미 가입된 이메일이에요.", "error")
            return render_template("register.html", form=f)

        cur = conn.execute(
            """INSERT INTO users (email, password_hash, name, gender, birth_year, location)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email, generate_password_hash(password), name, gender,
             int(birth_year), location),
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()

        session["user_id"] = user_id
        flash("환영해요! 가치관·취향 설문을 완성하면 추천이 시작돼요.", "success")
        return redirect(url_for("onboarding"))

    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
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
    conn = get_db()
    uid = session["user_id"]
    if request.method == "POST":
        for q in QUESTIONS:
            if q["type"] == "multi":
                vals = request.form.getlist(q["id"])
                value = ",".join(vals)
            else:
                value = request.form.get(q["id"], "")
            if value:
                conn.execute(
                    """INSERT INTO answers (user_id, question_id, value)
                       VALUES (?, ?, ?)
                       ON CONFLICT(user_id, question_id)
                       DO UPDATE SET value = excluded.value""",
                    (uid, q["id"], value),
                )
        conn.execute("UPDATE users SET onboarded = 1 WHERE id = ?", (uid,))
        conn.commit()
        conn.close()
        flash("설문이 저장됐어요. 맞는 상대를 찾아볼까요?", "success")
        return redirect(url_for("home"))

    answers = get_answers(conn, uid)
    conn.close()
    return render_template("onboarding.html", questions=QUESTIONS, answers=answers)


@app.route("/home")
@login_required
def home():
    me = current_user()
    if not me["onboarded"]:
        flash("먼저 가치관·취향 설문을 완성해 주세요.", "info")
        return redirect(url_for("onboarding"))

    conn = get_db()
    my_answers = get_answers(conn, me["id"])

    # 이미 좋아요 누른 상대
    liked = {
        r["to_user"]
        for r in conn.execute(
            "SELECT to_user FROM likes WHERE from_user = ?", (me["id"],)
        ).fetchall()
    }

    # 반대 성별, 온보딩 완료, 본인 제외, 아직 좋아요 안 한 사람
    target_gender = "F" if me["gender"] == "M" else "M"
    candidates = conn.execute(
        """SELECT * FROM users
           WHERE id != ? AND onboarded = 1 AND gender = ?""",
        (me["id"], target_gender),
    ).fetchall()

    results = []
    for c in candidates:
        if c["id"] in liked:
            continue
        c_answers = get_answers(conn, c["id"])
        score = match_score(my_answers, c_answers)
        shared = shared_highlights(my_answers, c_answers)
        results.append({"user": c, "match": score, "shared": shared})

    conn.close()
    results.sort(key=lambda r: r["match"]["score"], reverse=True)
    return render_template("home.html", results=results)


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    me = current_user()
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        abort(404)

    my_answers = get_answers(conn, me["id"])
    their_answers = get_answers(conn, user_id)
    score = match_score(my_answers, their_answers)

    # 답변을 카테고리별로 정리(라벨 포함)
    grouped = {"values": [], "taste": []}
    for q in QUESTIONS:
        val = their_answers.get(q["id"])
        if not val:
            continue
        if q["type"] == "multi":
            labels = [option_label(q["id"], k) for k in val.split(",") if k]
            display = ", ".join(labels)
        else:
            display = option_label(q["id"], val)
        same = False
        mine = my_answers.get(q["id"])
        if mine and q["type"] != "multi":
            same = mine == val
        grouped[q["category"]].append(
            {"text": q["text"], "display": display, "same": same}
        )

    already_liked = conn.execute(
        "SELECT 1 FROM likes WHERE from_user = ? AND to_user = ?",
        (me["id"], user_id),
    ).fetchone() is not None
    likes_me = conn.execute(
        "SELECT 1 FROM likes WHERE from_user = ? AND to_user = ?",
        (user_id, me["id"]),
    ).fetchone() is not None
    conn.close()

    is_match = already_liked and likes_me
    return render_template(
        "profile.html", user=user, match=score, grouped=grouped,
        already_liked=already_liked, is_match=is_match, likes_me=likes_me,
    )


@app.route("/like/<int:user_id>", methods=["POST"])
@login_required
def like(user_id):
    me = current_user()
    if user_id == me["id"]:
        abort(400)
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO likes (from_user, to_user) VALUES (?, ?)",
        (me["id"], user_id),
    )
    conn.commit()
    mutual = conn.execute(
        "SELECT 1 FROM likes WHERE from_user = ? AND to_user = ?",
        (user_id, me["id"]),
    ).fetchone() is not None
    conn.close()
    if mutual:
        flash("서로 좋아요! 매칭이 성사됐어요 💛", "success")
    else:
        flash("좋아요를 보냈어요.", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/matches")
@login_required
def matches():
    me = current_user()
    conn = get_db()
    my_answers = get_answers(conn, me["id"])
    rows = conn.execute(
        """SELECT u.* FROM users u
           JOIN likes l1 ON l1.to_user = u.id AND l1.from_user = ?
           JOIN likes l2 ON l2.from_user = u.id AND l2.to_user = ?""",
        (me["id"], me["id"]),
    ).fetchall()
    results = []
    for u in rows:
        u_answers = get_answers(conn, u["id"])
        score = match_score(my_answers, u_answers)
        shared = shared_highlights(my_answers, u_answers)
        results.append({"user": u, "match": score, "shared": shared})
    conn.close()
    results.sort(key=lambda r: r["match"]["score"], reverse=True)
    return render_template("matches.html", results=results)


@app.route("/me", methods=["GET", "POST"])
@login_required
def me_page():
    me = current_user()
    conn = get_db()
    if request.method == "POST":
        bio = request.form.get("bio", "").strip()
        location = request.form.get("location", "").strip()
        conn.execute(
            "UPDATE users SET bio = ?, location = ? WHERE id = ?",
            (bio, location, me["id"]),
        )
        conn.commit()
        flash("프로필이 저장됐어요.", "success")
        conn.close()
        return redirect(url_for("me_page"))

    my_answers = get_answers(conn, me["id"])
    grouped = {"values": [], "taste": []}
    for q in QUESTIONS:
        val = my_answers.get(q["id"])
        if not val:
            continue
        if q["type"] == "multi":
            display = ", ".join(option_label(q["id"], k) for k in val.split(",") if k)
        else:
            display = option_label(q["id"], val)
        grouped[q["category"]].append({"text": q["text"], "display": display})
    conn.close()
    return render_template("me.html", grouped=grouped)


if __name__ == "__main__":
    # 로컬 개발용 실행 (배포 시에는 gunicorn app:app 사용)
    # host='0.0.0.0' : 같은 와이파이의 폰/태블릿에서도 접속 가능
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
