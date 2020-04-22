"""
SQLAlchemy models for database
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from candig_cnv_service.orm import Base
from candig_cnv_service.orm.custom_types import GUID, JsonArray, TimeStamp


class Dataset(Base):
    """
    SQLAlchemy class representing a Dataset
    """

    __tablename__ = "dataset"

    dataset_id = Column(GUID(), primary_key=True)
    sample_id = relationship("Sample")
    name = Column(String(100))


class Sample(Base):
    """
    SQLAlchemy class representing a Sample tied to a Dataset
    """

    __tablename__ = "sample"

    sample_id = Column(String(100), primary_key=True)
    dataset_id = Column(
        GUID(), ForeignKey("dataset.dataset_id"), nullable=False
    )
    tags = Column(JsonArray(), default=[])
    access_level = Column(Integer)
    description = Column(String(100), unique=True, nullable=False)
    created = Column(TimeStamp())
    cnv_id = relationship("CNV")


class CNV(Base):
    """
    SQLAlchemy class representing a collection of Copy Number
    Variants, all tied to a Sample
    """

    __tablename__ = "cnv"
    # cnv_id = Column(Integer, primary_key=True)

    sample_id = Column(
        String(100), ForeignKey("sample.sample_id"), primary_key=True
    )
    start_position = Column(Integer, primary_key=True)
    end_position = Column(Integer)
    copy_number = Column(Float)
    copy_number_ploidy_corrected = Column(Integer)
    chromosome = Column(String(100), primary_key=True)
