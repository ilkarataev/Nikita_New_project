from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
# from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyBaseOAuthAccountTable

Base = declarative_base()

class User(Base):
    __tablename__ = "users"  # Match the table name expected by SQLAlchemyBaseUserTable
    # Define additional columns here
    id = Column(Integer, primary_key=True, autoincrement=True)  # Определение первичного ключа
    last_name = Column(String(50), nullable=True, index=True)
    first_name = Column(String(50), nullable=True, index=True)
    email = Column(String(50), nullable=False, index=True)
    password = Column(Text, nullable=False)
    reg_date = Column(DateTime, nullable=False)
    balance = Column(Float, nullable=False, default=0)
    status = Column(String(50), nullable=True)
    work_status = Column(String(50), nullable=True)
    group = Column(String(50), nullable=True)
    # balance = relationship("Balance", back_populates="user", uselist=False)
    api_requests = relationship("ApiRequest", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id})>"

class ApiRequest(Base):
    __tablename__ = "api_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    request_date = Column(DateTime, nullable=False)
    original_width = Column(Integer, nullable=False)
    original_height = Column(Integer, nullable=False)
    upscale_width = Column(Integer, nullable=False)
    upscale_height = Column(Integer, nullable=False)
    scale_factor = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    user = relationship("User", back_populates="api_requests")

    def __repr__(self):
        return f"<ApiRequest(id={self.id}, request_date={self.request_date}, price={self.price})>"

class ImageUpscalePrice(Base):
    __tablename__ = "image_upscale_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_width = Column(Integer, nullable=False)
    original_height = Column(Integer, nullable=False)
    upscale_width = Column(Integer, nullable=False)
    upscale_height = Column(Integer, nullable=False)
    scale_factor = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<ImageUpscalePrice(id={self.id}, original={self.original_width}x{self.original_height}, upscale={self.upscale_width}x{self.upscale_height}, scale_factor={self.scale_factor}, price={self.price})>"