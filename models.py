"""
AIMS ERP Models
Sprint 1 - Minimal Models
"""

from sqlalchemy import Column, Integer
from database import Base


class HealthCheck(Base):
    __tablename__ = "health_check"

    id = Column(Integer, primary_key=True)
