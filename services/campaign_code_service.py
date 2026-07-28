from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.campaign import Campaign


class CampaignCodeService:

    PREFIX = "CMP"
    
    @staticmethod
    def generate(db: Session) -> str:
        
        return "CMP-2026-000001"
