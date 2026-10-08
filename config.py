"""설정 한 곳에 모으기. 비밀값(DB 비밀번호·JWT 키·API 키)은 코드에 쓰지 않고
같은 폴더의 .env 에서 읽는다. .env 는 절대 깃에 올리지 않는다(.gitignore).
제출·공유용으로는 .env.example 만 남긴다."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # .env → 환경변수 (import 시점 1회)


class Config:
    # ── 데이터베이스 (도커 MySQL) ──
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── 로그인 토큰 ──
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # ── 보안 이벤트 REST (n8n 이 호출) ──
    # 값이 비어 있으면 POST 는 항상 401 (fail-closed: 실수로 열어두지 않는다)
    SECURITY_API_KEY = os.environ.get('SECURITY_API_KEY', '')
    # 거부(deny) 시 게시판에 '보안' 공지글 자동 등록: 1=켬, 0=끔
    AUTO_POST_ON_DENY = os.environ.get('AUTO_POST_ON_DENY', '0') == '1'

    # ── 관리자 API (회수봇·n8n 이 X-API-Key 로 호출) ──
    # 값이 비어 있으면 기계 경로는 항상 401 (fail-closed). 사람은 JWT+role=admin 으로 대체 접근.
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', '')
    # 관리자 등급을 가져도 되는 허용목록 — 회수봇이 이 목록 '밖'의 admin 을 과잉권한으로 판단한다.
    ADMIN_ALLOWLIST = [u.strip() for u in os.environ.get('ADMIN_ALLOWLIST', '').split(',') if u.strip()]

    # ── Graylog(GELF) — 허용목록 밖 admin 부여 시 즉시 신고 ──
    GRAYLOG_HOST = os.environ.get('GRAYLOG_HOST', 'localhost')
    GRAYLOG_GELF_PORT = int(os.environ.get('GRAYLOG_GELF_PORT', '12201'))
    STUDENT_NAME = os.environ.get('STUDENT_NAME', 'unknown')

    # ── 보안 로그 파일(Wazuh 에이전트가 읽음) — 비우면 write_seclog()가 조용히 끔 ──
    SECURITY_LOG_PATH = os.environ.get(
        'SECURITY_LOG_PATH',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'security.log'))

    # ── 공공데이터(부산 테마여행) ──
    PUBLIC_API_KEY = os.environ.get('PUBLIC_API_KEY')
    PUBLIC_API_URL = "https://apis.data.go.kr/6260000/RecommendedService/getRecommendedKr"
