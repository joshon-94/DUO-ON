"""듀온 - 가치관/취향 설문 정의 및 매칭 점수 계산

각 질문:
  id      : 고유키 (answers 테이블 question_id 로 저장)
  category: 'values'(가치관) / 'taste'(취향)
  text    : 화면 표시 문구
  type    : 'single'(단일선택) / 'multi'(복수선택)
  options : [(키, 라벨), ...]
  weight  : 매칭 점수 가중치 (가치관이 더 높음)
"""

QUESTIONS = [
    # ===== 가치관 (values) =====
    {
        "id": "marriage",
        "category": "values",
        "text": "어떤 만남을 찾고 있나요?",
        "type": "single",
        "weight": 4,
        "options": [
            ("serious", "결혼을 전제로 한 진지한 만남"),
            ("relationship", "좋은 사람이면 천천히 연애부터"),
            ("casual", "부담 없이 가볍게 알아가기"),
        ],
    },
    {
        "id": "children",
        "category": "values",
        "text": "자녀 계획에 대한 생각은?",
        "type": "single",
        "weight": 4,
        "options": [
            ("want", "아이를 원해요"),
            ("none", "아이 계획은 없어요"),
            ("undecided", "아직 잘 모르겠어요"),
        ],
    },
    {
        "id": "religion",
        "category": "values",
        "text": "종교가 있나요?",
        "type": "single",
        "weight": 3,
        "options": [
            ("none", "무교"),
            ("christian", "기독교"),
            ("catholic", "천주교"),
            ("buddhist", "불교"),
            ("etc", "기타"),
        ],
    },
    {
        "id": "drink",
        "category": "values",
        "text": "음주는 어느 정도 하나요?",
        "type": "single",
        "weight": 2,
        "options": [
            ("often", "즐기는 편"),
            ("sometimes", "가끔 마셔요"),
            ("none", "거의 안 마셔요"),
        ],
    },
    {
        "id": "smoke",
        "category": "values",
        "text": "흡연을 하나요?",
        "type": "single",
        "weight": 3,
        "options": [
            ("yes", "흡연"),
            ("no", "비흡연"),
        ],
    },
    {
        "id": "lifestyle",
        "category": "values",
        "text": "평소 라이프스타일은?",
        "type": "single",
        "weight": 2,
        "options": [
            ("home", "집에서 보내는 게 좋아요"),
            ("active", "밖에서 활동하는 게 좋아요"),
            ("balanced", "그때그때 반반"),
        ],
    },
    {
        "id": "money",
        "category": "values",
        "text": "경제관은 어느 쪽에 가까운가요?",
        "type": "single",
        "weight": 2,
        "options": [
            ("save", "저축·미래 대비 우선"),
            ("enjoy", "현재의 삶을 즐기기"),
            ("balanced", "균형 있게"),
        ],
    },
    # ===== 취향 (taste) =====
    {
        "id": "hobbies",
        "category": "taste",
        "text": "관심 있는 취미를 모두 골라주세요.",
        "type": "multi",
        "weight": 2,
        "options": [
            ("sports", "운동"),
            ("travel", "여행"),
            ("movie", "영화/드라마"),
            ("music", "음악"),
            ("reading", "독서"),
            ("game", "게임"),
            ("cooking", "요리"),
            ("art", "미술/전시"),
            ("cafe", "카페/맛집"),
            ("pet", "반려동물"),
        ],
    },
    {
        "id": "travel_style",
        "category": "taste",
        "text": "여행 스타일은?",
        "type": "single",
        "weight": 1,
        "options": [
            ("plan", "계획형"),
            ("spontaneous", "즉흥형"),
            ("relax", "휴양 위주"),
            ("active", "액티비티 위주"),
        ],
    },
    {
        "id": "weekend",
        "category": "taste",
        "text": "이상적인 주말은?",
        "type": "single",
        "weight": 1,
        "options": [
            ("rest", "집에서 푹 쉬기"),
            ("friends", "친구들과 약속"),
            ("hobby", "취미 활동"),
            ("date", "연인과 데이트"),
        ],
    },
    {
        "id": "mbti",
        "category": "taste",
        "text": "MBTI를 알려주세요. (선택)",
        "type": "single",
        "weight": 1,
        "options": [
            (m, m)
            for m in [
                "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP",
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP",
            ]
        ],
    },
]

# 빠른 조회용 인덱스
QUESTION_MAP = {q["id"]: q for q in QUESTIONS}


def option_label(question_id, key):
    q = QUESTION_MAP.get(question_id)
    if not q:
        return key
    for k, label in q["options"]:
        if k == key:
            return label
    return key


def match_score(answers_a: dict, answers_b: dict):
    """두 사용자의 답변 dict({question_id: value}) 로 매칭 점수(0~100)와
    카테고리별 세부 점수를 반환한다."""
    total_weight = 0.0
    earned = 0.0
    cat_weight = {"values": 0.0, "taste": 0.0}
    cat_earned = {"values": 0.0, "taste": 0.0}

    for q in QUESTIONS:
        a = answers_a.get(q["id"])
        b = answers_b.get(q["id"])
        # 한쪽이라도 답을 안 했으면 점수 계산에서 제외(공정성)
        if not a or not b:
            continue
        w = q["weight"]
        total_weight += w
        cat_weight[q["category"]] += w

        if q["type"] == "multi":
            set_a = set(filter(None, a.split(",")))
            set_b = set(filter(None, b.split(",")))
            if set_a or set_b:
                sim = len(set_a & set_b) / len(set_a | set_b)
            else:
                sim = 0.0
            gained = w * sim
        else:
            gained = w if a == b else 0.0

        earned += gained
        cat_earned[q["category"]] += gained

    if total_weight == 0:
        return {"score": 0, "values": 0, "taste": 0}

    def pct(e, t):
        return round(e / t * 100) if t else 0

    return {
        "score": pct(earned, total_weight),
        "values": pct(cat_earned["values"], cat_weight["values"]),
        "taste": pct(cat_earned["taste"], cat_weight["taste"]),
    }


def shared_highlights(answers_a: dict, answers_b: dict, limit=3):
    """두 사람의 공통점(같은 답/겹치는 취미) 라벨을 짧게 추려 반환.
    가치관을 먼저, 그다음 취향 순으로 채운다."""
    out = []
    for q in QUESTIONS:
        a = answers_a.get(q["id"])
        b = answers_b.get(q["id"])
        if not a or not b:
            continue
        if q["type"] == "multi":
            common = [k for k in a.split(",") if k and k in b.split(",")]
            for k in common:
                out.append(option_label(q["id"], k))
        elif a == b:
            out.append(option_label(q["id"], a))
    # 중복 제거, 순서 유지
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq[:limit]
