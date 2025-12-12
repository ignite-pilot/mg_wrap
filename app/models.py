from app import db
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import TypeDecorator, String

class EnumType(TypeDecorator):
    """PostgreSQL ENUM과 호환되는 Enum 타입"""
    impl = String
    cache_ok = True
    
    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)

class StorageType(PyEnum):
    SPACE = 'space'
    BOX = 'box'

class ApplicationStatus(PyEnum):
    PENDING = 'pending'
    APPROVED = 'approved'
    ACTIVE = 'active'
    COMPLETED = 'completed'

class AssetCategory(PyEnum):
    OFFICE_SUPPLIES = 'office_supplies'
    DOCUMENTS = 'documents'
    EQUIPMENT = 'equipment'
    FURNITURE = 'furniture'
    CLOTHING = 'clothing'
    APPLIANCES = 'appliances'
    OTHER = 'other'

class AssetStatus(PyEnum):
    STORED = 'stored'
    RETRIEVAL_REQUESTED = 'retrieval_requested'
    RETRIEVAL_CANCELLED = 'retrieval_cancelled'
    RETRIEVED = 'retrieved'
    DISPOSAL_REQUESTED = 'disposal_requested'
    DISPOSAL_CANCELLED = 'disposal_cancelled'
    DISPOSED = 'disposed'

class RetrievalStatus(PyEnum):
    PREPARING = 'preparing'
    IN_TRANSIT = 'in_transit'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class DisposalStatus(PyEnum):
    PREPARING = 'preparing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

# User 모델 제거 - ig-member 서비스를 사용
# user_id는 ig-member의 사용자 ID를 저장 (Integer)

class StorageApplication(db.Model):
    __tablename__ = 'storage_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # ig-member의 사용자 ID
    storage_type = db.Column(EnumType(StorageType), nullable=False)
    space_pyeong = db.Column(db.Integer, nullable=True)
    box_count = db.Column(db.Integer, nullable=True)
    months = db.Column(db.Integer, nullable=False)
    estimated_price = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(EnumType(ApplicationStatus), default=ApplicationStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assets = db.relationship('Asset', backref='storage_application', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'storage_type': self.storage_type.value if self.storage_type else None,
            'space_pyeong': self.space_pyeong,
            'box_count': self.box_count,
            'months': self.months,
            'estimated_price': float(self.estimated_price) if self.estimated_price else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_number = db.Column(db.String(50), unique=True, nullable=False)
    storage_application_id = db.Column(db.Integer, db.ForeignKey('storage_applications.id'), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    storage_start_date = db.Column(db.Date, nullable=True)
    asset_category = db.Column(EnumType(AssetCategory), nullable=False)
    special_notes = db.Column(db.Text, nullable=True)
    status = db.Column(EnumType(AssetStatus), default=AssetStatus.STORED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    retrieval_request = db.relationship('RetrievalRequest', backref='asset', uselist=False, lazy=True)
    disposal_request = db.relationship('DisposalRequest', backref='asset', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_number': self.asset_number,
            'storage_application_id': self.storage_application_id,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'storage_start_date': self.storage_start_date.isoformat() if self.storage_start_date else None,
            'asset_category': self.asset_category.value if self.asset_category else None,
            'special_notes': self.special_notes,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RetrievalRequest(db.Model):
    __tablename__ = 'retrieval_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    status = db.Column(EnumType(RetrievalStatus), default=RetrievalStatus.PREPARING)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset': self.asset.to_dict() if self.asset else None,
            'status': self.status.value if self.status else None,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DisposalRequest(db.Model):
    __tablename__ = 'disposal_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    status = db.Column(EnumType(DisposalStatus), default=DisposalStatus.PREPARING)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset': self.asset.to_dict() if self.asset else None,
            'status': self.status.value if self.status else None,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

