from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=True, index=True)
    first_name = Column(String(50), nullable=True, index=True)
    email = Column(String(50), nullable=False, index=True)
    password = Column(Text, nullable=False)
    reg_date = Column(DateTime, nullable=False)
    balance = Column(Float, nullable=False, default=0)
    status = Column(String(50), nullable=True)
    work_status = Column(String(50), nullable=True)
    group = Column(String(50), nullable=True)
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
    scale_factor = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    task_id = Column(String(250), nullable=True)
    user = relationship("User", back_populates="api_requests")

    def __repr__(self):
        return f"<ApiRequest(id={self.id})>"

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
        return f"<ImageUpscalePrice(id={self.id})>"