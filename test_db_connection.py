#!/usr/bin/env python3
"""데이터베이스 연결 테스트"""
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    try:
        print("Testing database connection...")
        count = User.query.count()
        print("✓ Database connection OK")
        print(f"✓ User count: {count}")
        
        # 테스트 사용자 생성 시도
        test_user = User(
            google_id='test_connection_check',
            email='test@test.com',
            name='Test User'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✓ User creation test: OK")
        
        # 삭제
        db.session.delete(test_user)
        db.session.commit()
        print("✓ User deletion test: OK")
        
    except Exception as e:
        import traceback
        print(f"✗ Database Error: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")

