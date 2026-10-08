"""회원가입 / 로그인 / 내 정보(등급 확인)."""
import json
import socket
import time

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import client_ip, db
from models import User

from .seclog import write_seclog

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _report_login_failure_to_graylog(username, ip, locked=False):
    """로그인 실패마다 GELF로 Graylog에 신고 — 같은 src_ip에서 반복되면 Graylog가 집계해 n8n에 알린다.
    locked=True 면 이미 잠긴 계정에 재시도한 것 — [114] 인시던트 승격 룰(locked:1)이 이 필드를 본다."""
    payload = {
        'version': '1.1',
        'host': socket.gethostname(),
        'short_message': f"login failure: '{username}' from {ip}",
        'timestamp': time.time(),
        'level': 5,
        '_rule': 'login-bruteforce',
        '_username': username,
        '_src_ip': ip,
        '_locked': 1 if locked else 0,
    }
    data = json.dumps(payload).encode('utf-8')
    host = current_app.config.get('GRAYLOG_HOST', 'localhost')
    port = current_app.config.get('GRAYLOG_GELF_PORT', 12201)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(data, (host, port))
    except OSError:
        pass


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "이미 존재하는 사용자입니다."}), 400

    hashed_password = generate_password_hash(data['password'])
    # 가입은 항상 일반(user) 등급 — 등급 상승은 관리자 페이지에서만.
    new_user = User(username=data['username'], password=hashed_password, role='user')
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "회원가입 성공"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.locked:
        _report_login_failure_to_graylog(data.get('username', ''), client_ip(), locked=True)
        write_seclog('login_failed', data.get('username') or '(unknown)', client_ip())
        return jsonify({"msg": "잠긴 계정입니다(관리자에게 문의).", "locked": True}), 423
    if not user or not check_password_hash(user.password, data['password']):
        _report_login_failure_to_graylog(data.get('username', ''), client_ip())
        write_seclog('login_failed', data.get('username') or '(unknown)', client_ip())
        return jsonify({"msg": "아이디 또는 비밀번호가 잘못되었습니다."}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, **user.to_dict())


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """현재 로그인한 사용자의 최신 등급 — 등급이 바뀐 뒤 재로그인 없이 화면 분기에 쓴다."""
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"msg": "사용자를 찾을 수 없습니다."}), 404
    return jsonify(user.to_dict())
