"""골드 등급 전용 API — @role_required('gold') 하나로 서버가 직접 차단한다(화면 숨김이 아니라).
골드 미만 403, 미로그인 401. 주소창에 이 URL 을 직접 쳐도 등급이 없으면 그대로 막힌다."""
from flask import Blueprint, jsonify

from controllers.rbac import role_required
from models import Post

gold_bp = Blueprint('gold', __name__, url_prefix='/api/gold')


@gold_bp.route('/posts', methods=['GET'])
@role_required('gold')
def gold_posts():
    """골드 이상만 보는 전용 게시글(카테고리='골드전용')."""
    posts = (Post.query.filter_by(category='골드전용')
             .order_by(Post.id.desc()).limit(20).all())
    return jsonify({'posts': [p.to_dict() for p in posts]})
