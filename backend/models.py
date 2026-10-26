from sqlalchemy import Column, Integer, String, Float
# from database import Base

class ThresholdSettings(Base):
    __tablename__ = "threshold_settings"
    id = Column(Integer, primary_key=True, index=True)
    fish_type = Column(String, default="Tilapia")
    ph_norm_min = Column(Float, default=6.5)
    ph_norm_max = Column(Float, default=8.5)
    ph_danger_min = Column(Float, default=5.0)
    ph_danger_max = Column(Float, default=10.0)
    temp_norm_min = Column(Float, default=26.0)
    temp_norm_max = Column(Float, default=30.0)
    temp_danger_min = Column(Float, default=20.0)
    temp_danger_max = Column(Float, default=35.0)
    turb_norm_max = Column(Float, default=300.0)
    turb_danger_max = Column(Float, default=500.0)