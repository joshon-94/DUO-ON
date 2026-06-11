"""듀온 - 테스트용 샘플 회원 생성 (Flask-SQLAlchemy)

앱 시작 시 일반 회원이 없으면 자동으로 run()이 호출돼요.
직접 실행하려면:  python seed.py
비밀번호는 모두 'test1234' 입니다.
"""
from werkzeug.security import generate_password_hash

from models import db, User

SAMPLE_USERS = [
    {
        "email": "minji@example.com", "name": "민지", "gender": "F",
        "birth_year": 1995, "location": "서울 마포구",
        "bio": "주말엔 전시 보러 다니는 걸 좋아해요.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "balanced",
            "money": "balanced", "hobbies": "art,cafe,travel",
            "travel_style": "plan", "weekend": "hobby", "mbti": "INFJ",
        },
    },
    {
        "email": "seoyeon@example.com", "name": "서연", "gender": "F",
        "birth_year": 1993, "location": "서울 송파구",
        "bio": "운동하고 맛집 찾아다니는 게 취미예요!",
        "answers": {
            "marriage": "relationship", "children": "undecided", "religion": "none",
            "drink": "often", "smoke": "no", "lifestyle": "active",
            "money": "enjoy", "hobbies": "sports,cafe,music",
            "travel_style": "active", "weekend": "friends", "mbti": "ENFP",
        },
    },
    {
        "email": "jihu@example.com", "name": "지후", "gender": "M",
        "birth_year": 1992, "location": "서울 강남구",
        "bio": "조용히 책 읽는 시간을 좋아하는 사람입니다.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "home",
            "money": "save", "hobbies": "reading,movie,cafe",
            "travel_style": "plan", "weekend": "rest", "mbti": "INTJ",
        },
    },
    {
        "email": "junseo@example.com", "name": "준서", "gender": "M",
        "birth_year": 1994, "location": "서울 용산구",
        "bio": "여행 다니며 사진 찍는 걸 좋아해요.",
        "answers": {
            "marriage": "relationship", "children": "undecided", "religion": "none",
            "drink": "often", "smoke": "no", "lifestyle": "active",
            "money": "enjoy", "hobbies": "travel,sports,music,cafe",
            "travel_style": "active", "weekend": "friends", "mbti": "ESTP",
        },
    },
    {
        "email": "haeun@example.com", "name": "하은", "gender": "F",
        "birth_year": 1996, "location": "경기 성남시",
        "bio": "집에서 영화 보고 요리하는 걸 좋아합니다.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "catholic",
            "drink": "none", "smoke": "no", "lifestyle": "home",
            "money": "save", "hobbies": "cooking,movie,reading,pet",
            "travel_style": "relax", "weekend": "rest", "mbti": "ISFJ",
        },
    },
    {
        "email": "taeyang@example.com", "name": "태양", "gender": "M",
        "birth_year": 1991, "location": "서울 마포구",
        "bio": "전시 보고 카페 가는 데이트 좋아해요.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "balanced",
            "money": "balanced", "hobbies": "art,cafe,travel,reading",
            "travel_style": "plan", "weekend": "hobby", "mbti": "INFP",
        },
    },
]


def run():
    """샘플 회원을 추가한다. (이미 있으면 건너뜀)"""
    pw = generate_password_hash("test1234")
    for u in SAMPLE_USERS:
        if User.query.filter_by(email=u["email"]).first():
            continue
        user = User(
            email=u["email"], password_hash=pw, name=u["name"],
            gender=u["gender"], birth_year=u["birth_year"],
            location=u["location"], bio=u["bio"], onboarded=True,
        )
        user.set_answers(u["answers"])
        db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    from app import app
    with app.app_context():
        run()
    print("샘플 회원 생성 완료. 비밀번호는 모두 'test1234' 입니다.")
