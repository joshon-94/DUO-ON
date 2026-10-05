"""Vercel 서버리스 진입점.

Vercel의 Python 런타임이 이 파일의 `app`(WSGI)을 찾아 실행한다.
실제 애플리케이션은 저장소 루트의 app.py에 있다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
