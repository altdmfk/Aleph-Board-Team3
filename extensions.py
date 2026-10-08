"""확장(Extension) 객체를 한 곳에서 만든다.
app 과 분리해 두면 models·controllers 어디서든 import 해도
순환 참조(circular import)가 생기지 않는다."""
from flask import request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()


def client_ip():
    """프록시(n8n·nginx) 뒤면 X-Forwarded-For 첫 값, 아니면 remote_addr.
    (랩 환경 — 실서비스는 신뢰 프록시 목록으로 검증해야 스푸핑을 막는다.)"""
    xff = request.headers.get('X-Forwarded-For', '')
    return xff.split(',')[0].strip() if xff else (request.remote_addr or '')
