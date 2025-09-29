"""
Enterprise Database Service
PostgreSQL connection and corporate data management
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import asyncpg
from datetime import datetime
import os

logger = logging.getLogger('chattoner.enterprise_db')

class EnterpriseDBService:
    """Enterprise database service"""
    
    def __init__(self, database_url: str = None):
        # Get DATABASE_URL from .env or use default value
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://user:password@localhost:5432/chattoner-db'
        )
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("DB 연결 풀 초기화 완료")
        except Exception as e:
            logger.error(f"DB 연결 실패: {e}")
            raise
    
    async def close(self):
        """Terminate database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("DB 연결 풀 종료")
    
    # Company profile management
    async def get_company_profile(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Query company profile"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow("""
                    SELECT company_id, company_name, industry, team_size, 
                           primary_business, communication_style, main_channels, 
                           target_audience, generated_profile, created_at
                    FROM company_profiles 
                    WHERE company_id = $1
                """, company_id)
                
                if row:
                    return {
                        'company_id': row['company_id'],
                        'company_name': row['company_name'],
                        'industry': row['industry'],
                        'team_size': row['team_size'],
                        'primary_business': row['primary_business'],
                        'communication_style': row['communication_style'],
                        'main_channels': json.loads(row['main_channels']) if row['main_channels'] else [],
                        'target_audience': json.loads(row['target_audience']) if row['target_audience'] else [],
                        'generated_profile': row['generated_profile'],
                        'created_at': row['created_at']
                    }
                return None
                
            except Exception as e:
                logger.error(f"기업 프로필 조회 실패 ({company_id}): {e}")
                return None
    
    async def get_company_guidelines(self, company_id: str) -> List[Dict[str, Any]]:
        """Query company guideline documents"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch("""
                    SELECT id, document_type, document_name, document_content,
                           processed_chunks, uploaded_by, created_at
                    FROM communication_guidelines 
                    WHERE company_id = $1 AND is_active = true
                    ORDER BY created_at DESC
                """, company_id)
                
                guidelines = []
                for row in rows:
                    guidelines.append({
                        'id': row['id'],
                        'document_type': row['document_type'],
                        'document_name': row['document_name'],
                        'document_content': row['document_content'],
                        'processed_chunks': json.loads(row['processed_chunks']) if row['processed_chunks'] else [],
                        'uploaded_by': row['uploaded_by'],
                        'created_at': row['created_at']
                    })
                
                logger.info(f"기업 가이드라인 조회 완료 ({company_id}): {len(guidelines)}개")
                return guidelines
                
            except Exception as e:
                logger.error(f"기업 가이드라인 조회 실패 ({company_id}): {e}")
                return []
    
    async def get_user_preferences(self, user_id: str, company_id: str) -> Optional[Dict[str, Any]]:
        """Query user company-specific preferences"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow("""
                    SELECT personal_style, negative_prompts, preference_weights,
                           created_at, updated_at
                    FROM user_company_preferences 
                    WHERE user_id = $1 AND company_id = $2 AND is_active = true
                """, user_id, company_id)
                
                if row:
                    return {
                        'personal_style': json.loads(row['personal_style']) if row['personal_style'] else {},
                        'negative_prompts': row['negative_prompts'],
                        'preference_weights': json.loads(row['preference_weights']) if row['preference_weights'] else {},
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                return None
                
            except Exception as e:
                logger.error(f"사용자 선호도 조회 실패 ({user_id}, {company_id}): {e}")
                return None
    
    async def save_learning_data(self, learning_data: Dict[str, Any]) -> bool:
        """Store learning data"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO company_learning_data 
                    (company_id, user_id, input_text, output_text, context, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                    learning_data.get('company_id'),
                    learning_data.get('user_id'),
                    learning_data.get('input_text'),
                    learning_data.get('output_text', ''),  # Set as empty value
                    json.dumps(learning_data.get('context', {})),
                    datetime.now()
                )
                
                logger.info(f"학습 데이터 저장 완료 ({learning_data.get('company_id')})")
                return True
                
            except Exception as e:
                logger.error(f"학습 데이터 저장 실패: {e}")
                return False
    
    async def save_user_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Store user feedback"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO company_user_feedback 
                    (user_id, company_id, session_id, original_text, suggested_text,
                     feedback_type, feedback_value, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    feedback_data.get('user_id'),
                    feedback_data.get('company_id'),
                    feedback_data.get('session_id'),
                    feedback_data.get('original_text'),
                    feedback_data.get('suggested_text'),
                    feedback_data.get('feedback_type'),  # 'grammar' or 'protocol'
                    feedback_data.get('feedback_value'), # 'good' or 'bad'
                    json.dumps(feedback_data.get('metadata', {})),
                    datetime.now()
                )
                
                logger.info(f"사용자 피드백 저장 완료")
                return True
                
            except Exception as e:
                logger.error(f"사용자 피드백 저장 실패: {e}")
                return False
    
    # Test and development methods
    async def create_test_company(self, company_id: str = "test_company") -> bool:
        """Create test company data"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            try:
                # Create company profile
                await conn.execute("""
                    INSERT INTO company_profiles 
                    (company_id, company_name, industry, team_size, primary_business,
                     communication_style, main_channels, target_audience, generated_profile)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (company_id) DO NOTHING
                """,
                    company_id,
                    "테스트 회사",
                    "IT",
                    50,
                    "소프트웨어 개발",
                    "formal",
                    json.dumps(["email", "slack", "reports"]),
                    json.dumps(["internal", "clients"]),
                    "정중하고 전문적인 커뮤니케이션을 지향합니다. 클라이언트 대상 문서는 특히 격식을 갖추어 작성해야 합니다."
                )
                
                # Create guideline documents
                await conn.execute("""
                    INSERT INTO communication_guidelines
                    (company_id, document_type, document_name, document_content, is_active)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT DO NOTHING
                """,
                    company_id,
                    "manual_input",
                    "커뮤니케이션 가이드",
                    """
1. 모든 대외 문서는 존댓말을 사용합니다.
2. 이메일 제목에는 [중요도]를 표시합니다.
3. 회의록은 다음 구조를 따릅니다: 참석자, 안건, 결정사항, 액션아이템
4. 클라이언트 대상 문서는 '고객님'으로 호칭합니다.
5. 금지 용어: '대박', '쩔어', '헐' 등 비격식 표현
                    """,
                    True
                )
                
                logger.info(f"테스트 기업 데이터 생성 완료: {company_id}")
                return True
                
            except Exception as e:
                logger.error(f"테스트 기업 데이터 생성 실패: {e}")
                return False
    
    async def check_connection(self) -> bool:
        """DB 연결 확인"""
        try:
            if not self.pool:
                await self.initialize()
                
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                logger.info("DB 연결 확인 완료")
                return result == 1
                
        except Exception as e:
            logger.error(f"DB 연결 확인 실패: {e}")
            return False

# Manage DB service with singleton pattern
_enterprise_db_service = None

async def get_enterprise_db_service() -> EnterpriseDBService:
    """Return global DB service instance"""
    global _enterprise_db_service
    
    if _enterprise_db_service is None:
        _enterprise_db_service = EnterpriseDBService()
        await _enterprise_db_service.initialize()
    
    return _enterprise_db_service

# Use DB service with context manager
class EnterpriseDBContext:
    """DB 서비스 컨텍스트 매니저"""
    
    def __init__(self, database_url: str = None):
        self.db_service = EnterpriseDBService(database_url)
    
    async def __aenter__(self):
        await self.db_service.initialize()
        return self.db_service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db_service.close()

# Usage example and test functions
async def test_enterprise_db():
    """DB 서비스 테스트"""
    async with EnterpriseDBContext() as db:
        # Check connection
        is_connected = await db.check_connection()
        print(f"DB 연결: {is_connected}")
        
        # Create test data
        await db.create_test_company("test_company")
        
        # Data query test
        profile = await db.get_company_profile("test_company")
        print(f"기업 프로필: {profile}")
        
        guidelines = await db.get_company_guidelines("test_company")
        print(f"가이드라인 개수: {len(guidelines)}")

if __name__ == "__main__":
    # Execute test
    asyncio.run(test_enterprise_db())