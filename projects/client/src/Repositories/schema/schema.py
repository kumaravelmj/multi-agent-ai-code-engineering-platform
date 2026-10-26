from sqlalchemy import Column, Integer,text, Text, DateTime, String, ForeignKey, Boolean,CheckConstraint,Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
Base = declarative_base()

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    function_name = Column(String(255), nullable=False)
    error = Column(Text, nullable=False)
    err_code = Column(String(20), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False, default="system")
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(String(100), nullable=False, default="system")