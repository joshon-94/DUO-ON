"""듀온 - 테스트용 샘플 회원 생성 (Flask-SQLAlchemy)

앱 시작 시 일반 회원이 없으면 자동으로 run()이 호출돼요.
직접 실행하려면:  python seed.py
비밀번호는 모두 'test1234' 입니다.

사진은 static/photos/ 에 포함된 AI 생성 아시아계(한국형) 얼굴을 사용합니다.
(generated.photos 무료 AI 얼굴) 관리자 페이지에서 언제든 바꿀 수 있어요.
"""
from werkzeug.security import generate_password_hash

from models import db, User

MAN = "/static/photos/m%d.jpg"
WOMAN = "/static/photos/w%d.jpg"

SAMPLE_USERS = [
    {
        "email": "minji@example.com", "name": "민지", "gender": "F",
        "birth_year": 1995, "location": "서울 마포구", "photo": WOMAN % 1,
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
        "birth_year": 1993, "location": "서울 송파구", "photo": WOMAN % 2,
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
        "birth_year": 1992, "location": "서울 강남구", "photo": MAN % 1,
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
        "birth_year": 1994, "location": "서울 용산구", "photo": MAN % 2,
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
        "birth_year": 1996, "location": "경기 성남시", "photo": WOMAN % 3,
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
        "birth_year": 1991, "location": "서울 마포구", "photo": MAN % 3,
        "bio": "전시 보고 카페 가는 데이트 좋아해요.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "balanced",
            "money": "balanced", "hobbies": "art,cafe,travel,reading",
            "travel_style": "plan", "weekend": "hobby", "mbti": "INFP",
        },
    },
    {
        "email": "suijn@example.com", "name": "수진", "gender": "F",
        "birth_year": 1994, "location": "서울 서초구", "photo": WOMAN % 4,
        "bio": "캠핑이랑 등산 좋아하는 액티브한 사람이에요.",
        "answers": {
            "marriage": "relationship", "children": "undecided", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "active",
            "money": "balanced", "hobbies": "sports,travel,pet",
            "travel_style": "active", "weekend": "friends", "mbti": "ESFP",
        },
    },
    {
        "email": "yerin@example.com", "name": "예린", "gender": "F",
        "birth_year": 1997, "location": "인천 연수구", "photo": WOMAN % 5,
        "bio": "음악 듣고 카페에서 책 읽는 게 행복이에요.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "none", "smoke": "no", "lifestyle": "balanced",
            "money": "save", "hobbies": "music,reading,cafe",
            "travel_style": "plan", "weekend": "hobby", "mbti": "INFP",
        },
    },
    {
        "email": "daeun@example.com", "name": "다은", "gender": "F",
        "birth_year": 1992, "location": "서울 종로구", "photo": WOMAN % 6,
        "bio": "맛있는 거 먹으러 다니는 미식가입니다.",
        "answers": {
            "marriage": "relationship", "children": "no", "religion": "none",
            "drink": "often", "smoke": "no", "lifestyle": "active",
            "money": "enjoy", "hobbies": "cooking,cafe,music,travel",
            "travel_style": "active", "weekend": "friends", "mbti": "ENFJ",
        },
    },
    {
        "email": "hyunwoo@example.com", "name": "현우", "gender": "M",
        "birth_year": 1990, "location": "서울 강서구", "photo": MAN % 4,
        "bio": "헬스랑 러닝으로 하루를 시작해요.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "christian",
            "drink": "sometimes", "smoke": "no", "lifestyle": "active",
            "money": "save", "hobbies": "sports,music,travel",
            "travel_style": "plan", "weekend": "hobby", "mbti": "ESTJ",
        },
    },
    {
        "email": "doyun@example.com", "name": "도윤", "gender": "M",
        "birth_year": 1995, "location": "경기 수원시", "photo": MAN % 5,
        "bio": "게임이랑 영화, 가끔 캠핑 다녀요.",
        "answers": {
            "marriage": "relationship", "children": "undecided", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "home",
            "money": "balanced", "hobbies": "movie,music,cooking",
            "travel_style": "relax", "weekend": "rest", "mbti": "ISTP",
        },
    },
    {
        "email": "siwoo@example.com", "name": "시우", "gender": "M",
        "birth_year": 1993, "location": "서울 성동구", "photo": MAN % 6,
        "bio": "전시랑 공연 보러 다니는 걸 좋아합니다.",
        "answers": {
            "marriage": "serious", "children": "want", "religion": "none",
            "drink": "sometimes", "smoke": "no", "lifestyle": "balanced",
            "money": "balanced", "hobbies": "art,music,reading,cafe",
            "travel_style": "plan", "weekend": "hobby", "mbti": "INFJ",
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
            location=u["location"], bio=u["bio"],
            photo_url=u.get("photo", ""), onboarded=True,
        )
        user.set_answers(u["answers"])
        db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    from app import app
    with app.app_context():
        run()
    print("샘플 회원 생성 완료. 비밀번호는 모두 'test1234' 입니다.")
