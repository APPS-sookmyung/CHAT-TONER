import logging
from typing import Dict, Any, List, Optional
from database.storage import DatabaseStorage

logger = logging.getLogger('chattoner.enterprise_db')

class EnterpriseDBService:
    def __init__(self):
        self.storage = DatabaseStorage()

    async def get_company_profile(self, company_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get_company_profile(company_id)

    async def upsert_company_profile(
        self,
        company_id: str,
        company_name: str,
        industry: str,
        team_size: int,
        primary_business: str,
        communication_style: str,
        main_channels: List[str],
        target_audience: List[str],
        generated_profile: str,
        survey_data: Dict[str, Any]
    ) -> bool:
        profile_data = {
            "company_id": company_id,
            "company_name": company_name,
            "industry": industry,
            "team_size": team_size,
            "primary_business": primary_business,
            "communication_style": communication_style,
            "main_channels": main_channels,
            "target_audience": target_audience,
            "generated_profile": generated_profile,
            "survey_data": survey_data,
        }
        return self.storage.save_company_profile(profile_data)

