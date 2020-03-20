from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from candig_cnv_service.orm import Base
from candig_cnv_service.orm.guid import GUID


class Patient(Base):
    __tablename__ = "patient"

    patient_id = Column(GUID(), primary_key=True)
    sample_id = relationship("sample")


class Sample(Base):
    __tablename__ = "sample"

    sample_id = Column(String(100), primary_key=True)
    patient_id = Column(GUID(), ForeignKey("patient.patient_id"))
    cnv_id = relationship("cnv")


class CNV(Base):
    __tablename__ = "cnv"
    cnv_id = Column(Integer, primary_key=True)
    sample_id = Column(String(100), ForeignKey("sample.sample_id"))
    start_position = Column(Integer)
    end_position = Column(Integer)
    copy_number = Column(Float)
    copy_number_ploidy_correcte = Column(Integer)
    chromosome_number = Column(String(100))
