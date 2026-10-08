"""공용 인가 판정기 — 등급이 필요한 라우트에 붙이는 데코레이터 딱 하나.
인가 검사를 이 한 곳에 모아둬야 나중에 등급을 늘려도(gold 추가 등) 라우트마다 고칠 필요가 없다.
401 vs 403: 401 = 로그인 자체가 안 됨("네가 누구인지 모른다"), 403 = 로그인은 됐지만 등급이 모자람
("누구인지는 알지만 그 등급은 안 된다"). 화면에서 메뉴를 숨기는 건 보안이 아니므로,
실제 차단은 항상 이 데코레이터가 서버에서 한다."""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User


def role_required(required):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = User.query.get(int(get_jwt_identity()))
            if not user or not user.has_role(required):
                return jsonify({
                    'msg': f'{required} 등급 이상만 접근할 수 있습니다.',
                    'required_role': required,
                    'current_role': user.role if user else None,
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
