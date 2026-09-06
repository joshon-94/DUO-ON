"""카카오톡 '나에게 보내기' 알림용 refresh token 발급 도우미.

준비 (한 번만):
  1) https://developers.kakao.com → 내 애플리케이션 → 애플리케이션 추가하기
  2) [앱 설정 > 앱 키]에서 'REST API 키' 복사
  3) [카카오 로그인] 활성화 ON
  4) [카카오 로그인 > Redirect URI]에 아래 REDIRECT_URI 값을 그대로 등록
  5) [카카오 로그인 > 동의항목]에서 '카카오톡 메시지 전송(talk_message)' 사용 설정

사용:
  1) REST_API_KEY 를 아래에 채우거나 환경변수 KAKAO_REST_API_KEY 로 넣는다.
  2) python kakao_token.py            → 인증 URL이 출력됨. 브라우저로 접속해 로그인/동의.
  3) 이동된 주소창의 code=... 값(URL의 code 파라미터)을 복사.
  4) python kakao_token.py <code>     → refresh_token 이 출력됨.
  5) Render 환경변수에 KAKAO_REST_API_KEY, KAKAO_REFRESH_TOKEN 등록 후 재배포.
"""
import os
import sys
import requests

REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "여기에_REST_API_키_붙여넣기")
REDIRECT_URI = "https://duon.onrender.com/oauth"  # 카카오 콘솔에 동일하게 등록


def auth_url():
    return (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=talk_message"
    )


def exchange(code):
    res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
        timeout=10,
    )
    data = res.json()
    print("\n[응답]", data)
    if "refresh_token" in data:
        print("\n=== Render 환경변수에 넣으세요 ===")
        print("KAKAO_REST_API_KEY =", REST_API_KEY)
        print("KAKAO_REFRESH_TOKEN =", data["refresh_token"])
    else:
        print("\n토큰 발급 실패. REST_API_KEY / Redirect URI / 동의항목 설정을 확인하세요.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("1) 아래 주소를 브라우저에서 열어 로그인/동의하세요:\n")
        print(auth_url())
        print("\n2) 이동된 주소의 code=... 값을 복사해서:")
        print("   python kakao_token.py <code>")
    else:
        exchange(sys.argv[1])
