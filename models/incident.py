from datetime import datetime

from extensions import db


class Incident(db.Model):
    """출발지(src_ip) 기준으로 취합된 보안 인시던트 티켓."""
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    src_ip = db.Column(db.String(45), index=True)
    severity = db.Column(db.String(10), default='Medium')          # Low|Medium|High|Critical
    status = db.Column(db.String(12), default='open', index=True)  # open|closed
    summary = db.Column(db.Text)              # 자동 취합된 사람이 읽는 요약
    event_count = db.Column(db.Integer, default=0)
    actions = db.Column(db.String(255))       # 취해진 조치(deny/allow 등)
    student = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    closed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'src_ip': self.src_ip,
            'severity': self.severity,
            'status': self.status,
            'summary': self.summary,
            'event_count': self.event_count,
            'actions': self.actions,
            'student': self.student,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
        }
