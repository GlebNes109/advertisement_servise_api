import uuid

from .api_models import Campaign, Targeting
from .db_models import CampaignDB


def convert_to_apimodel(db_model):
    if isinstance(db_model, CampaignDB):
        targeting = Targeting(
            gender=db_model.targeting_gender,
            age_from=db_model.targeting_age_from,
            age_to=db_model.targeting_age_to,
            location=db_model.targeting_location
        )
        api_model = Campaign(
            campaign_id=db_model.campaign_id,
            advertiser_id=db_model.advertiser_id,
            impressions_limit=db_model.impressions_limit,
            clicks_limit=db_model.clicks_limit,
            cost_per_impression=db_model.cost_per_impression,
            cost_per_click=db_model.cost_per_click,
            ad_title=db_model.ad_title,
            ad_text=db_model.ad_text,
            start_date=db_model.start_date,
            end_date=db_model.end_date,
            targeting=targeting
        )
        return api_model.model_dump()


class ModelConvertionError(Exception):
    pass

def convert_to_dbmodel(apimodel, advertiserId=None):
    if isinstance(apimodel, Campaign) and advertiserId:
        campaign_db = CampaignDB(
            campaign_id=str(uuid.uuid4()),
            advertiser_id=advertiserId,
            impressions_limit=apimodel.impressions_limit,
            clicks_limit=apimodel.clicks_limit,
            cost_per_impression=apimodel.cost_per_impression,
            cost_per_click=apimodel.cost_per_click,
            ad_title=apimodel.ad_title,
            ad_text=apimodel.ad_text,
            start_date=apimodel.start_date,
            end_date=apimodel.end_date,
            targeting_gender=apimodel.targeting.gender,
            targeting_age_from=apimodel.targeting.age_from,
            targeting_age_to=apimodel.targeting.age_to,
            targeting_location=apimodel.targeting.location
        )

        return campaign_db

"""def convert_campaigncreate_to_campaign(campaign_create: CampaignCreate, campaign_id, advertiserId):
    campaign = Campaign(
        campaign_id=campaign_id,
        advertiser_id=advertiserId,
        impressions_limit=campaign_create.impressions_limit,
        clicks_limit=campaign_create.clicks_limit,
        cost_per_impression=campaign_create.cost_per_impression,
        cost_per_click=campaign_create.cost_per_click,
        ad_title=campaign_create.ad_title,
        ad_text=campaign_create.ad_text,
        start_date=campaign_create.start_date,
        end_date=campaign_create.end_date,
        targeting=Targeting() # у Campaign эта секция должна быть по-любому
    )

    if campaign_create.targeting:
        campaign.targeting.gender = campaign_create.targeting.gender
        campaign.targeting.age_to = campaign_create.targeting.age_to
        campaign.targeting.age_from = campaign_create.targeting.age_from
        campaign.targeting.location = campaign_create.targeting.location

    return campaign
"""