"""SQLAlchemy models — see docs/ARCHITECTURE.md Section 5 for the shape.

TODO(backend): pick sync vs async engine and wire this up in database.py.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    text = Column(Text, nullable=False)
    embedding_vector = Column(Text, nullable=True)



class CallJob(Base):
    __tablename__ = "call_jobs"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    caller_number = Column(String, nullable=False)
    # TODO(backend): pending -> in_progress -> completed / failed
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class CallResult(Base):
    __tablename__ = "call_results"

    id = Column(Integer, primary_key=True)
    call_job_id = Column(Integer, ForeignKey("call_jobs.id"), nullable=False)
    question_asked = Column(Text)
    answer_given = Column(Text)
    resolved = Column(Boolean, default=False)
    needs_human_followup = Column(Boolean, default=False)
    transcript_url = Column(String, nullable=True)

class TelephonyEvent(Base):
    __tablename__ = "telephony_events"

    id = Column(Integer, primary_key=True)
    provider_event_id = Column(String, nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    business_number = Column(String, nullable=False)
    caller_number = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)