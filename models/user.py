from extensions import db

# 계단식 3등급(RBAC) — 숫자가 클수록 강함. "필요 등급보다 내 등급이 같거나 높으면 통과".
ROLE_LEVEL = {'user': 1, 'gold': 2, 'admin': 3}
ROLE_LABEL = {'user': '일반', 'gold': '골드', 'admin': '관리자'}


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # 해시만 저장(평문 금지)
    role = db.Column(db.String(20), nullable=False, default='user')
    # ── 감사 추적(4-2) — 누가·언제·왜 등급을 바꿨는지. 사람이 매번 확인하기 어려우니 남겨 둔다.
    role_granted_by = db.Column(db.String(80))
    role_granted_at = db.Column(db.DateTime)
    role_reason = db.Column(db.String(255))
    # ── 계정 잠금(brute-force 대응) ──
    locked = db.Column(db.Boolean, nullable=False, default=False)
    locked_reason = db.Column(db.String(200))
    locked_at = db.Column(db.DateTime)

    def role_level(self):
        """모르는 등급 값(오탈자·DB 오염)은 0 = 가장 안전한 실패로 취급한다."""
        return ROLE_LEVEL.get(self.role, 0)

    def has_role(self, required):
        """내 등급 ≥ required 면 통과. admin 은 gold 전용 화면도 그대로 통과(계단식)."""
        return self.role_level() >= ROLE_LEVEL.get(required, 999)

    @property
    def is_gold(self):
        return self.has_role('gold')

    @property
    def is_admin(self):
        return self.has_role('admin')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'role_label': ROLE_LABEL.get(self.role, self.role),
            'is_gold': self.is_gold,
            'is_admin': self.is_admin,
            'role_granted_by': self.role_granted_by,
            'role_granted_at': self.role_granted_at.isoformat() if self.role_granted_at else None,
            'role_reason': self.role_reason,
            'locked': self.locked,
            'locked_reason': self.locked_reason,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
