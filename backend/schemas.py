from pydantic import BaseModel

class ThresholdSettingsBase(BaseModel):
    fish_type: str
    ph_norm_min: float
    ph_norm_max: float
    ph_danger_min: float
    ph_danger_max: float
    temp_norm_min: float
    temp_norm_max: float
    temp_danger_min: float
    temp_danger_max: float
    turb_norm_max: float
    turb_danger_max: float

class ThresholdSettingsResponse(ThresholdSettingsBase):
    id: int
    class Config:
        orm_mode = True