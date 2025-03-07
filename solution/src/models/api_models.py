from typing import Optional
from pydantic import BaseModel
from enum import Enum
from sqlmodel import Field

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class GenderTarget(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"

class ClientUpsert(BaseModel):
    client_id: str
    login: str
    age: int
    location: str
    gender: Gender

class AdvertiserUpsert(BaseModel):
    advertiser_id: str
    name: str

class MLScore(BaseModel):
    client_id: str
    advertiser_id: str
    score: int

class Targeting(BaseModel):
    gender: Optional[GenderTarget] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    location: Optional[str] = None

class CampaignCreate(BaseModel):
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    targeting: Optional[Targeting] = None

class Campaign(BaseModel):
    campaign_id: str
    advertiser_id: str
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    targeting: Targeting

class CampaignUpdate(BaseModel):
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    targeting: Optional[Targeting]=None

class Ad(BaseModel):
    ad_id: str
    ad_title: str
    ad_text: str
    advertiser_id: str

class RequestDay(BaseModel):
    current_date: int = Field(ge=0)

class Blacklist(BaseModel):
    ban_words: list[str]

class Click_clientId(BaseModel):
    client_id: str

class Stats(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float

class DailyStats(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float
    date: int