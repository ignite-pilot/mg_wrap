"""
데이터베이스 초기화 스크립트
"""
from app import create_app, db
from app.models import *  # noqa: F403 - SQLAlchemy 모델 등록을 위해 필요

app = create_app()

with app.app_context():
    print("데이터베이스 테이블 생성 중...")
    db.create_all()
    print("완료!")

