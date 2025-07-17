"""
Database models and operations for the parking system
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Boolean, Text, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class TransactionStatus(Enum):
    """Transaction status enumeration"""
    MASUK = "MASUK"
    KELUAR = "KELUAR" 
    BATAL = "BATAL"


class MemberStatus(Enum):
    """Member status enumeration"""
    AKTIF = "AKTIF"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"


class VehicleType(Base):
    """Vehicle type configuration"""
    __tablename__ = 'vehicle_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    tarif_awal = Column(Float, default=0.0)
    tarif_berikutnya = Column(Float, default=0.0) 
    tarif_maksimal = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="vehicle_type")


class Member(Base):
    """Member information"""
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    member_id = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    license_plate = Column(String(20), index=True)
    status = Column(String(20), default=MemberStatus.AKTIF.value)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="member")
    
    # Indexes
    __table_args__ = (
        Index('idx_member_license_plate', 'license_plate'),
        Index('idx_member_phone', 'phone'),
        Index('idx_member_status', 'status'),
    )


class Transaction(Base):
    """Parking transactions"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(50), nullable=False, unique=True, index=True)
    license_plate = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default=TransactionStatus.MASUK.value)
    
    # Vehicle information
    vehicle_type_id = Column(Integer, ForeignKey('vehicle_types.id'))
    
    # Member information
    member_id = Column(Integer, ForeignKey('members.id'), nullable=True)
    is_member = Column(Boolean, default=False)
    
    # Time tracking
    waktu_masuk = Column(DateTime, default=datetime.utcnow)
    waktu_keluar = Column(DateTime, nullable=True)
    
    # Financial
    tarif = Column(Float, default=0.0)
    payment_amount = Column(Float, default=0.0)
    
    # Images (base64 encoded)
    entry_pic = Column(Text, nullable=True)  # Plate image at entry
    driver_pic = Column(Text, nullable=True)  # Driver image at entry
    exit_pic = Column(Text, nullable=True)   # Plate image at exit
    
    # Gate information
    entry_gate_id = Column(String(50))
    exit_gate_id = Column(String(50))
    
    # Staff information
    entry_staff = Column(String(100))
    exit_staff = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle_type = relationship("VehicleType", back_populates="transactions")
    member = relationship("Member", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_license_plate', 'license_plate'),
        Index('idx_transaction_status', 'status'),
        Index('idx_transaction_waktu_masuk', 'waktu_masuk'),
        Index('idx_transaction_member', 'member_id'),
    )


class GateSettings(Base):
    """Gate configuration settings"""
    __tablename__ = 'gate_settings'
    
    id = Column(Integer, primary_key=True)
    gate_id = Column(String(50), nullable=False, unique=True)
    gate_type = Column(String(20), nullable=False)  # 'entry' or 'exit'
    gate_mode = Column(String(20), nullable=False)  # 'manual' or 'manless'
    
    # Camera settings
    plate_cam_type = Column(String(10))  # 'usb' or 'cctv'
    plate_cam_device_id = Column(Integer)
    plate_cam_ip = Column(String(100))
    plate_cam_username = Column(String(50))
    plate_cam_password = Column(String(50))
    plate_cam_snapshot_path = Column(String(200))
    
    driver_cam_type = Column(String(10))
    driver_cam_device_id = Column(Integer)
    driver_cam_ip = Column(String(100))
    driver_cam_username = Column(String(50))
    driver_cam_password = Column(String(50))
    driver_cam_snapshot_path = Column(String(200))
    
    # ALPR settings
    use_external_alpr = Column(Boolean, default=False)
    alpr_websocket_url = Column(String(200))
    alpr_confidence_threshold = Column(Float, default=0.7)
    
    # Serial port settings
    serial_port = Column(String(20))
    serial_baudrate = Column(Integer, default=9600)
    
    # General settings
    settings_json = Column(Text)  # JSON field for additional settings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """Activity logging for gates"""
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    gate_id = Column(String(50), nullable=False)
    level = Column(String(20), default='INFO')  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON details
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_gate_id', 'gate_id'),
        Index('idx_activity_timestamp', 'timestamp'),
        Index('idx_activity_level', 'level'),
    )


class DatabaseManager:
    """Database manager for async operations"""
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///parking_system.db"):
        self.database_url = database_url
        self.async_engine = None
        self.async_session = None
        self.sync_engine = None
        self.sync_session = None
    
    async def initialize(self):
        """Initialize database connections"""
        try:
            # Async engine for main operations
            self.async_engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            self.async_session = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Sync engine for initial setup
            sync_url = self.database_url.replace("+aiosqlite", "")
            self.sync_engine = create_engine(sync_url, echo=False)
            self.sync_session = sessionmaker(self.sync_engine)
            
            # Create tables
            await self.create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables"""
        try:
            # Use sync engine for table creation
            Base.metadata.create_all(self.sync_engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        return self.async_session()
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        logger.info("Database connections closed")


class TransactionRepository:
    """Transaction database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        async with self.db_manager.get_session() as session:
            transaction = Transaction(**transaction_data)
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            return transaction
    
    async def get_transaction_by_ticket_id(self, ticket_id: str) -> Optional[Transaction]:
        """Get transaction by ticket ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                f"SELECT * FROM transactions WHERE ticket_id = '{ticket_id}'"
            )
            return result.scalar_one_or_none()
    
    async def get_transaction_by_license_plate(self, license_plate: str, 
                                              status: str = TransactionStatus.MASUK.value) -> Optional[Transaction]:
        """Get active transaction by license plate"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                f"SELECT * FROM transactions WHERE license_plate = '{license_plate}' AND status = '{status}' ORDER BY waktu_masuk DESC LIMIT 1"
            )
            return result.scalar_one_or_none()
    
    async def update_transaction(self, transaction_id: int, update_data: Dict[str, Any]) -> bool:
        """Update transaction"""
        async with self.db_manager.get_session() as session:
            try:
                transaction = await session.get(Transaction, transaction_id)
                if transaction:
                    for key, value in update_data.items():
                        setattr(transaction, key, value)
                    transaction.updated_at = datetime.utcnow()
                    await session.commit()
                    return True
                return False
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update transaction {transaction_id}: {e}")
                return False
    
    async def get_active_transactions(self) -> List[Transaction]:
        """Get all active (MASUK) transactions"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                f"SELECT * FROM transactions WHERE status = '{TransactionStatus.MASUK.value}' ORDER BY waktu_masuk DESC"
            )
            return result.scalars().all()


class MemberRepository:
    """Member database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def get_member_by_license_plate(self, license_plate: str) -> Optional[Member]:
        """Get member by license plate"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                f"SELECT * FROM members WHERE license_plate = '{license_plate}' AND status = '{MemberStatus.AKTIF.value}'"
            )
            return result.scalar_one_or_none()
    
    async def get_member_by_member_id(self, member_id: str) -> Optional[Member]:
        """Get member by member ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                f"SELECT * FROM members WHERE member_id = '{member_id}'"
            )
            return result.scalar_one_or_none()
    
    async def is_member_valid(self, member: Member) -> bool:
        """Check if member is valid (not expired)"""
        if member.status != MemberStatus.AKTIF.value:
            return False
        
        if member.valid_until and member.valid_until < datetime.utcnow():
            return False
        
        return True


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get or create the global database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    
    return _db_manager


async def get_transaction_repository() -> TransactionRepository:
    """Get transaction repository"""
    db_manager = await get_database_manager()
    return TransactionRepository(db_manager)


async def get_member_repository() -> MemberRepository:
    """Get member repository"""
    db_manager = await get_database_manager()
    return MemberRepository(db_manager)
