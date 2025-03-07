from typing import Optional

from sqlalchemy import LargeBinary
from sqlmodel import SQLModel, Field

class ClientDB(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    client_id: str = Field(primary_key=True)
    login: str
    age: int
    location: str
    gender: str

class AdvertiserDB(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    advertiser_id: str = Field(primary_key=True)
    name: str

class MLScoreDB(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    client_id: str
    advertiser_id: str
    score: int
    normalized_score: float

class CampaignDB(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    campaign_id: str = Field(primary_key=True)
    advertiser_id: str
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    clicks_used: int
    impressions_used: int
    targeting_gender: Optional[str] = None
    targeting_age_from: Optional[int] = None
    targeting_age_to: Optional[int] = None
    targeting_location: Optional[str] = None
    ad_image: Optional[bytes] = Field(default=None)

    model_config = {
        "arbitrary_types_allowed": True
    }

class AdsClicks(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    campaign_id: str
    client_id: str
    cost: float
    day: int

class AdsImpressions(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    campaign_id: str
    client_id: str
    cost: float
    day: int