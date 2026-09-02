"""듀온 - 데이터 모델 (Flask-SQLAlchemy)

로컬에서는 SQLite, 배포(Render)에서는 PostgreSQL을 자동으로 사용한다.
설문 답변은 별도 테이블 대신 users.answers_json(JSON 문자열)에 저장해 단순화.
"""
import json
import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(1))            # 'M' / 'F'
    birth_year = db.Column(db.Integer)
    location = db.Column(db.String(120), default="")
    bio = db.Column(db.Text, default="")
    photo_url = db.Column(db.Text, default="")  # 대표 사진 링크(첫 번째 사진)
    photos_json = db.Column(db.Text, default="[]")  # 사진 여러 장(URL 배열)
    answers_json = db.Column(db.Text, default="{}")
    onboarded = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # ----- 설문 답변 헬퍼 -----
    def get_answers(self) -> dict:
        try:
            return json.loads(self.answers_json or "{}")
        except (ValueError, TypeError):
            return {}

    def set_answers(self, data: dict):
        self.answers_json = json.dumps(data, ensure_ascii=False)

    # ----- 사진 여러 장 헬퍼 -----
    def get_photos(self) -> list:
        """사진 URL 목록. 구버전 photo_url만 있는 경우도 포함."""
        try:
            photos = json.loads(self.photos_json or "[]")
        except (ValueError, TypeError):
            photos = []
        if not photos and self.photo_url:
            photos = [self.photo_url]
        return [p for p in photos if p]

    def set_photos(self, urls: list):
        """사진 목록 저장 + 대표 사진(photo_url) 동기화."""
        clean = [u.strip() for u in urls if u and u.strip()]
        self.photos_json = json.dumps(clean, ensure_ascii=False)
        self.photo_url = clean[0] if clean else ""


class Like(db.Model):
    __tablename__ = "likes"

    from_user = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    to_user = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
