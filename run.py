from app import create_app, db
from app.models import *  # noqa: F403 - SQLAlchemy 모델 등록을 위해 필요

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # 단일 서비스로 통합: frontend와 backend를 하나의 포트에서 실행
    app.run(debug=True, host='0.0.0.0', port=8400)

