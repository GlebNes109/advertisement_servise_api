from sqlmodel import select, Session

from ..db.database import engine
from ..models.db_models import *
from ..models.api_models import *
import uuid

from sqlalchemy import text, func

class Repository:
    def __init__(self):
        SQLModel.metadata.create_all(engine)

    def add_client(self, client_db):
        with Session(engine) as session:
            session.add(client_db)
            session.commit()
            # session.refresh(client_db)

    def add_clients(self, clients_db):
        with Session(engine) as session:
            for client_db in clients_db:
                session.add(client_db)
            session.commit()
            # session.refresh(client_db)

    def check_clients(self, clients_id):
        with Session(engine) as session:
            query = select(ClientDB).where(ClientDB.client_id.in_(clients_id))
            result = session.exec(query).all()
            if result:
                return False

            else:
                return True
    
    def get_client_by_id(self, client_id):
        with Session(engine) as session:
            query = select(ClientDB).where(ClientDB.client_id == client_id)
            result = session.exec(query).first()
            return result

    def check_advertisers(self, advs_id):
        with Session(engine) as session:
            query = select(AdvertiserDB).where(AdvertiserDB.advertiser_id.in_(advs_id))
            result = session.exec(query).all()
            if result:
                return False

            else:
                return True

    def add_advertisers(self, advs_db):
        with Session(engine) as session:
            for advertiser_db in advs_db:
                session.add(advertiser_db)
            session.commit()

    def get_advertiser_by_id(self, advertiser_id):
        with Session(engine) as session:
            query = select(AdvertiserDB).where(AdvertiserDB.advertiser_id == advertiser_id)
            result = session.exec(query).first()
            return result

    def add_scrore(self, mlscore):
        #если есть скор клиент-рекламодатель его надо обновить а не добавить новый
        with Session(engine) as session:
            query = select(MLScoreDB).where(MLScoreDB.advertiser_id == mlscore.advertiser_id, MLScoreDB.client_id == mlscore.client_id)
            mlscore_db = session.exec(query).first()

            if mlscore_db:
               mlscore_db.score = mlscore.score
               session.commit()
               session.refresh(mlscore_db)

            else:
                mlscore_db = MLScoreDB(
                    id=str(uuid.uuid4()),
                    client_id=mlscore.client_id,
                    advertiser_id=mlscore.advertiser_id,
                    score=mlscore.score,
                    normalized_score=mlscore.score/10000
                )
                session.add(mlscore_db)
                session.commit()

            """normalize_query = text("update mlscoredb set normalized_score = score / cast((select max(score) from mlscoredb) as float);")
            session.exec(normalize_query)
            session.commit()""" # жалко что не работает из-за deadlock ов, идея пушка прям была, жаль что не заработало ((((

    def add_campaign(self, advertiserId, campaign_create):
        id = str(uuid.uuid4())
        campaign_db = CampaignDB(
            campaign_id=id,
            advertiser_id=advertiserId,
            impressions_limit=campaign_create.impressions_limit,
            clicks_limit=campaign_create.clicks_limit,
            cost_per_impression=campaign_create.cost_per_impression,
            cost_per_click=campaign_create.cost_per_click,
            ad_title=campaign_create.ad_title,
            ad_text=campaign_create.ad_text,
            start_date=campaign_create.start_date,
            end_date=campaign_create.end_date,
            clicks_used=0,
            impressions_used=0
        )

        if campaign_create.targeting: # таргет может быть не задан
            campaign_db.targeting_gender = campaign_create.targeting.gender
            campaign_db.targeting_age_from = campaign_create.targeting.age_from
            campaign_db.targeting_age_to = campaign_create.targeting.age_to
            campaign_db.targeting_location = campaign_create.targeting.location

        with Session(engine) as session:
            session.add(campaign_db)
            session.commit()
            session.refresh(campaign_db)

        return campaign_db

    def get_campaigns_with_pagination(self, advertiserId, limit, offset):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.advertiser_id == advertiserId).offset(offset).limit(limit)
            res = session.exec(query).all()
            return res

    def get_campaign(self, campaignId):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaignId)
            res = session.exec(query).first()
            return res

    def put_campaign(self, campaignId, advertiserId, campaign):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaignId)
            campaign_db = session.exec(query).first()
            if campaign_db:
                campaign_db.impressions_limit = campaign.impressions_limit or campaign_db.impressions_limit
                campaign_db.clicks_limit = campaign.clicks_limit or campaign_db.clicks_limit
                campaign_db.cost_per_impression = campaign.cost_per_impression or campaign_db.cost_per_impression
                campaign_db.cost_per_click = campaign.cost_per_click or campaign_db.cost_per_click
                campaign_db.ad_title = campaign.ad_title or campaign_db.ad_title
                campaign_db.ad_text = campaign.ad_text or campaign_db.ad_text

                if campaign.targeting:
                    campaign_db.targeting_gender = campaign.targeting.gender or campaign_db.targeting_gender
                    campaign_db.targeting_age_from = campaign.targeting.age_from or campaign_db.targeting_age_from
                    campaign_db.targeting_age_to = campaign.targeting.age_to or campaign_db.targeting_age_to
                    campaign_db.targeting_location = campaign.targeting.location or campaign_db.targeting_location

                session.commit()
                session.refresh(campaign_db)
                return campaign_db

    def delete_campaign(self, campaignId):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaignId)
            campaign = session.exec(query).first()
            if campaign:
                session.delete(campaign)
                session.commit()

    def get_crazy_querystring_for_ad(self):
        return text("""
            with d as (
                select c.campaign_id, c.ad_title, c.ad_text, c.advertiser_id, 
                c.cost_per_impression, c.cost_per_click, s.score, s.normalized_score,
                (c.cost_per_impression + s.normalized_score*c.cost_per_click)*2 + s.normalized_score as weight
                from campaigndb c
                join MLScoreDB s on s.advertiser_id = c.advertiser_id
                join clientdb cl on cl.client_id = s.client_id
                where  
                (c.targeting_gender is null or c.targeting_gender = 'ALL' or c.targeting_gender = cl.gender)
                AND (c.targeting_age_from is null or c.targeting_age_from <= cl.age)
                AND (c.targeting_age_to is null or c.targeting_age_to >= cl.age)
                AND (c.targeting_location is null or c.targeting_location = cl.location)
                AND c.start_date <= :curday
                AND c.end_date >= :curday
                AND cl.client_id = :client_id
                AND (impressions_used+1)<(impressions_limit+impressions_limit*0.1)
            )
            select campaign_id from d order by weight desc limit 1
        """)

    def get_ad(self, client_id, curday):
        with Session(engine) as session:
            query = self.get_crazy_querystring_for_ad()
            pars = {
                "curday": curday,
                "client_id": client_id
            }

            res = session.exec(query, params=pars).mappings().first()

            if res:  # если нашли объявление, сразу записать в статистику
                # если есть показ такого объявления, не добавлять в статистику показов
                query = select(AdsImpressions).where(AdsImpressions.campaign_id == res.campaign_id, AdsImpressions.client_id==client_id)
                campaign_db_exist = session.exec(query).first()

                if campaign_db_exist is None:
                    query = select(CampaignDB).where(CampaignDB.campaign_id == res.campaign_id)
                    campaign_db = session.exec(query).first()

                    imp = AdsImpressions(
                        id=str(uuid.uuid4()),
                        campaign_id=campaign_db.campaign_id,
                        client_id=client_id,
                        cost=campaign_db.cost_per_impression,
                        day=curday
                    )
                    session.add(imp)

                    campaign_db.impressions_used += 1

                    session.commit()
                    session.refresh(campaign_db)
                    return campaign_db
                else:
                    query = select(CampaignDB).where(CampaignDB.campaign_id == res.campaign_id)
                    campaign_db = session.exec(query).first()

                    # но счетчик показов не накручиваем для того же клиента
                    return campaign_db
            else:
                return None

    def click(self, campaign_db, client_id, curday):
        with Session(engine) as session:
            query = select(AdsClicks).where(AdsClicks.campaign_id == campaign_db.campaign_id,
                                                 AdsClicks.client_id == client_id)
            campaign_click_exist = session.exec(query).first()

            if campaign_click_exist is None:
                imp = AdsClicks(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign_db.campaign_id,
                    client_id=client_id,
                    cost=campaign_db.cost_per_click,
                    day=curday
                )
                session.add(imp)

                campaign_db = session.merge(campaign_db) # так как campaign_db получен в другой сессии
                campaign_db.clicks_used += 1

                session.commit()
                session.refresh(campaign_db)



    def aggregate_imp_and_clicks_stat(self, impstat, clickstat):
        # можно запросить статистику даже если не было показов и кликов
        impressions_count = impstat.impressions_count if impstat else 0
        spent_impressions = impstat.spent_impressions if impstat else 0

        clicks_count = clickstat.clicks_count if clickstat else 0
        spent_clicks = clickstat.spent_clicks if clickstat else 0

        conversion = round(clicks_count / impressions_count * 100, 2) if impressions_count > 0 else 0
        spent_total = round(spent_impressions + spent_clicks, 2)  # сумма трат на показы и клики

        stats = Stats(
            impressions_count=int(impressions_count),
            clicks_count=int(clicks_count),
            conversion=conversion,
            spent_impressions=round(spent_impressions, 2),
            spent_clicks=round(spent_clicks, 2),
            spent_total=spent_total
        )

        return stats



    def get_stats_campaign(self, campaign_id):
        with (Session(engine) as session):
            query = select(
                func.count().label("impressions_count"), # колво показов
                func.sum(AdsImpressions.cost).label("spent_impressions") # потрачено на показы
                ).where(AdsImpressions.campaign_id == campaign_id
                ).group_by(AdsImpressions.campaign_id)
            impstat = session.exec(query).first() # стата по показам

            query = select(
                func.count().label("clicks_count"),  # колво кликов
                func.sum(AdsClicks.cost).label("spent_clicks")  # потрачено на клики
                ).where(AdsClicks.campaign_id == campaign_id
                ).group_by(AdsClicks.campaign_id)
            clickstat = session.exec(query).first() # стата по кликам

            return self.aggregate_imp_and_clicks_stat(impstat, clickstat)

    def get_stats_campaign_daily(self, campaign_id):
        with (Session(engine) as session):
            query = select(
                func.count().label("impressions_count"), # колво показов
                func.sum(AdsImpressions.cost).label("spent_impressions"), # потрачено на показы
                AdsImpressions.day
                ).where(AdsImpressions.campaign_id == campaign_id
                ).group_by(AdsImpressions.campaign_id, AdsImpressions.day)
            impstat = session.exec(query).all() # стата по показам по дням

            query = select(
                func.count().label("clicks_count"),  # колво кликов
                func.sum(AdsClicks.cost).label("spent_clicks"),  # потрачено на клики
                AdsClicks.day
                ).where(AdsClicks.campaign_id == campaign_id
                ).group_by(AdsClicks.campaign_id, AdsClicks.day)
            clickstat = session.exec(query).all() # стата по кликам по дням

            # в дне может быть только клик или только показ - соберем уникальный список дней и отсортируем
            days_list = list(set([i.day for i in impstat] + [c.day for c in clickstat]))

            if days_list is None:
                return None

            dailyStats = []

            for day in days_list:
                imp_by_day = next((i for i in impstat if i.day == day), None) # показы в этом дне
                impressions_count = imp_by_day.impressions_count if imp_by_day else 0
                spent_impressions = imp_by_day.spent_impressions if imp_by_day else 0

                cl_by_day = next((c for c in clickstat if c.day == day), None)  # клики в этом дне
                clicks_count = cl_by_day.clicks_count if cl_by_day else 0
                spent_clicks = cl_by_day.spent_clicks if cl_by_day else 0

                conversion = round(clicks_count / impressions_count * 100, 2) if impressions_count > 0 else 0
                spent_total = round(spent_impressions + spent_clicks, 2)  # сумма трат на показы и клики

                stat = DailyStats(
                    impressions_count=int(impressions_count),
                    clicks_count=int(clicks_count),
                    conversion=conversion,
                    spent_impressions=round(spent_impressions, 2),
                    spent_clicks=round(spent_clicks, 2),
                    spent_total=spent_total,
                    date=day
                )
                dailyStats.append(stat)

            return dailyStats


    def get_stats_advertisers(self, advertiser_id):
        with (Session(engine) as session):
            query = select(
                func.count().label("impressions_count"),  # колво показов
                func.sum(AdsImpressions.cost).label("spent_impressions")  # потрачено на показы
                ).join(CampaignDB, CampaignDB.campaign_id == AdsImpressions.campaign_id
                ).where(CampaignDB.advertiser_id == advertiser_id
                ).group_by(CampaignDB.advertiser_id)
            impstat = session.exec(query).first()  # стата по показам

            query = select(
                func.count().label("clicks_count"),  # колво кликов
                func.sum(AdsClicks.cost).label("spent_clicks")  # потрачено на клики
                ).join(CampaignDB, CampaignDB.campaign_id == AdsClicks.campaign_id
                ).where(CampaignDB.advertiser_id == advertiser_id
                ).group_by(CampaignDB.advertiser_id)
            clickstat = session.exec(query).first() # стата по кликам

            return self.aggregate_imp_and_clicks_stat(impstat, clickstat)

    def get_stats_advertisers_daily(self, advertiser_id):
        with Session(engine) as session:
            query = select(
                func.count().label("impressions_count"),  # кол-во показов
                func.sum(AdsImpressions.cost).label("spent_impressions"),  # потрачено на показы
                AdsImpressions.day
            ).join(CampaignDB, CampaignDB.campaign_id == AdsImpressions.campaign_id
                   ).where(CampaignDB.advertiser_id == advertiser_id
                           ).group_by(AdsImpressions.day, CampaignDB.advertiser_id)
            impstat = session.exec(query).all()  # стата по показам по дням

            query = select(
                func.count().label("clicks_count"),  # кол-во кликов
                func.sum(AdsClicks.cost).label("spent_clicks"),  # потрачено на клики
                AdsClicks.day
            ).join(CampaignDB, CampaignDB.campaign_id == AdsClicks.campaign_id
                   ).where(CampaignDB.advertiser_id == advertiser_id
                           ).group_by(AdsClicks.day, CampaignDB.advertiser_id)
            clickstat = session.exec(query).all()  # стата по кликам по дням

            # return self.aggregate_imp_and_clicks_stat(impstat, clickstat)

            days_list = list(set([i.day for i in impstat] + [c.day for c in clickstat]))

            if not days_list:
                return None

            daily_stats = []
            for day in days_list:
                imp_by_day = next((i for i in impstat if i.day == day), None)  # показы в этом дне
                impressions_count = imp_by_day.impressions_count if imp_by_day else 0
                spent_impressions = imp_by_day.spent_impressions if imp_by_day else 0

                cl_by_day = next((c for c in clickstat if c.day == day), None)  # клики в этом дне
                clicks_count = cl_by_day.clicks_count if cl_by_day else 0
                spent_clicks = cl_by_day.spent_clicks if cl_by_day else 0

                conversion = round(clicks_count / impressions_count * 100, 2) if impressions_count > 0 else 0
                spent_total = round(spent_impressions + spent_clicks, 2)  # сумма трат на показы и клики

                stat = DailyStats(
                    impressions_count=int(impressions_count),
                    clicks_count=int(clicks_count),
                    conversion=conversion,
                    spent_impressions=round(spent_impressions, 2),
                    spent_clicks=round(spent_clicks, 2),
                    spent_total=spent_total,
                    date=day
                )
                daily_stats.append(stat)

            return daily_stats

    def add_image(self, image_data, campaign_id):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaign_id)
            campaign_db = session.exec(query).first()
            # campaign_db = session.get(CampaignDB, campaign_id)
            if campaign_db.ad_image:
                return False
            campaign_db.ad_image = image_data
            # session.add(campaign_db)
            session.commit()
            session.refresh(campaign_db)
            return True

    def delete_image(self, campaign_id):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaign_id)
            campaign_db = session.exec(query).first()
            # campaign_db = session.get(CampaignDB, campaign_id)
            campaign_db.ad_image = None
            # session.add(campaign_db)
            session.commit()
            session.refresh(campaign_db)
            return True

    def put_image(self, image_data, campaign_id):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaign_id)
            campaign_db = session.exec(query).first()
            # campaign_db = session.get(CampaignDB, campaign_id)
            if not campaign_db.ad_image:
                return False
            campaign_db.ad_image = image_data
            # session.add(campaign_db)
            session.commit()
            session.refresh(campaign_db)
            return True

    def get_image(self, campaign_id):
        with Session(engine) as session:
            query = select(CampaignDB).where(CampaignDB.campaign_id == campaign_id)
            campaign_db = session.exec(query).first()
            return campaign_db.ad_image

    def get_income_total(self):
        with Session(engine) as session:
            query = select(func.sum(AdsImpressions.cost))
            impstat = session.exec(query).first()  # стата по показам
            query = select(func.sum(AdsClicks.cost))
            clickstat = session.exec(query).first()
        return impstat, clickstat

    def get_advertiser_costs(self):
        with Session(engine) as session:
            query = (
                select(AdvertiserDB.name, func.sum(AdsImpressions.cost).label("sum"))
                .select_from(AdsImpressions)
                .join(CampaignDB, AdsImpressions.campaign_id == CampaignDB.campaign_id)
                .join(AdvertiserDB, AdvertiserDB.advertiser_id == CampaignDB.advertiser_id)
                .group_by(AdvertiserDB.name)
            )
            imps = session.exec(query).all()
            query = (
                select(AdvertiserDB.name, func.sum(AdsImpressions.cost).label("sum"))
                .select_from(AdsClicks)
                .join(CampaignDB, AdsClicks.campaign_id == CampaignDB.campaign_id)
                .join(AdvertiserDB, AdvertiserDB.advertiser_id == CampaignDB.advertiser_id)
                .group_by(AdvertiserDB.name)
            )
            clicks = session.exec(query).all()
            return imps, clicks