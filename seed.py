"""듀온 - 테스트용 샘플 회원 생성 스크립트

    python seed.py

비밀번호는 모두 'test1234' 이고, 이메일로 로그인하면 돼요.
"""
from werkzeug.security import generate_password_hash

from db import get_db, init_db

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
    init_db()
    conn = get_db()
    pw = generate_password_hash("test1234")
    for u in SAMPLE_USERS:
        exists = conn.execute(
            "SELECT id FROM users WHERE email = ?", (u["email"],)
        ).fetchone()
        if exists:
            print("이미 존재:", u["email"])
            continue
        cur = conn.execute(
            """INSERT INTO users (email, password_hash, name, gender, birth_year,
                                  location, bio, onboarded)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (u["email"], pw, u["name"], u["gender"], u["birth_year"],
             u["location"], u["bio"]),
        )
        uid = cur.lastrowid
        for qid, val in u["answers"].items():
            conn.execute(
                "INSERT INTO answers (user_id, question_id, value) VALUES (?, ?, ?)",
                (uid, qid, val),
            )
        print("생성:", u["name"], u["email"])
    conn.commit()
    conn.close()
    print("\n샘플 계정 비밀번호는 모두 'test1234' 입니다.")


if __name__ == "__main__":
    run()
