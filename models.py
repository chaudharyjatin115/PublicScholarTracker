from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Get database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PublicServant(Base):
    __tablename__ = "public_servants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department = Column(String)
    joining_year = Column(Integer)
    education_location = Column(String)
    university = Column(String)
    degree_level = Column(String)

    # One-to-many relationship with family members
    family_members = relationship("OfficerFamily", 
                                back_populates="officer",
                                cascade="all, delete-orphan")

class Politician(Base):
    __tablename__ = "politicians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    party = Column(String)
    position = Column(String)
    education_location = Column(String)
    university = Column(String)
    degree_level = Column(String)

    # One-to-many relationship with family members
    family_members = relationship("PoliticianFamily", 
                                back_populates="politician",
                                cascade="all, delete-orphan")

class PoliticianFamily(Base):
    __tablename__ = "politician_family"

    id = Column(Integer, primary_key=True, index=True)
    politician_id = Column(Integer, ForeignKey("politicians.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    relation_type = Column(String)
    education_location = Column(String)
    university = Column(String)
    degree_level = Column(String)

    # Many-to-one relationship with politician
    politician = relationship("Politician", back_populates="family_members")

class OfficerFamily(Base):
    __tablename__ = "officer_family"

    id = Column(Integer, primary_key=True, index=True)
    officer_id = Column(Integer, ForeignKey("public_servants.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    relation_type = Column(String)
    education_location = Column(String)
    university = Column(String)
    degree_level = Column(String)

    # Many-to-one relationship with officer
    officer = relationship("PublicServant", back_populates="family_members")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()