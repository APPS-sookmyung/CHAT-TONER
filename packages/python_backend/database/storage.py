import json
import logging
from typing import Dict, List, Optional, Any
from .sqlite_db import get_db_connection, create_tables

logger = logging.getLogger('chattoner.storage')


def _row_to_profile(row) -> Dict[str, Any]:
    """SQLite snake_case row를 API camelCase dict로 변환"""
    raw = dict(row)
    responses = raw.get("questionnaire_responses", "{}")
    if isinstance(responses, str):
        try:
            responses = json.loads(responses)
        except (json.JSONDecodeError, TypeError):
            responses = {}

    return {
        "id": raw.get("id"),
        "userId": raw.get("user_id"),
        "baseFormalityLevel": raw.get("base_formality_level", 3),
        "baseFriendlinessLevel": raw.get("base_friendliness_level", 3),
        "baseEmotionLevel": raw.get("base_emotion_level", 3),
        "baseDirectnessLevel": raw.get("base_directness_level", 3),
        "sessionFormalityLevel": raw.get("session_formality_level"),
        "sessionFriendlinessLevel": raw.get("session_friendliness_level"),
        "sessionEmotionLevel": raw.get("session_emotion_level"),
        "sessionDirectnessLevel": raw.get("session_directness_level"),
        "questionnaireResponses": responses,
        "createdAt": raw.get("created_at"),
        "updatedAt": raw.get("updated_at"),
    }


class DatabaseStorage:
    def __init__(self):
        create_tables()

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        conn.close()
        if profile:
            return _row_to_profile(profile)
        return None

    def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # responses 필드를 questionnaire_responses로 매핑
            responses_raw = profile_data.get('responses') or profile_data.get('questionnaireResponses', {})
            responses_json = json.dumps(responses_raw) if not isinstance(responses_raw, str) else responses_raw

            cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
            existing_profile = cursor.fetchone()
            if existing_profile:
                cursor.execute("""
                    UPDATE user_profiles
                    SET base_formality_level = ?, base_friendliness_level = ?, base_emotion_level = ?, base_directness_level = ?,
                        session_formality_level = ?, session_friendliness_level = ?, session_emotion_level = ?, session_directness_level = ?,
                        questionnaire_responses = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    profile_data.get('baseFormalityLevel', 3),
                    profile_data.get('baseFriendlinessLevel', 3),
                    profile_data.get('baseEmotionLevel', 3),
                    profile_data.get('baseDirectnessLevel', 3),
                    profile_data.get('sessionFormalityLevel'),
                    profile_data.get('sessionFriendlinessLevel'),
                    profile_data.get('sessionEmotionLevel'),
                    profile_data.get('sessionDirectnessLevel'),
                    responses_json,
                    user_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, base_formality_level, base_friendliness_level, base_emotion_level, base_directness_level,
                                           session_formality_level, session_friendliness_level, session_emotion_level, session_directness_level,
                                           questionnaire_responses)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    profile_data.get('baseFormalityLevel', 3),
                    profile_data.get('baseFriendlinessLevel', 3),
                    profile_data.get('baseEmotionLevel', 3),
                    profile_data.get('baseDirectnessLevel', 3),
                    profile_data.get('sessionFormalityLevel'),
                    profile_data.get('sessionFriendlinessLevel'),
                    profile_data.get('sessionEmotionLevel'),
                    profile_data.get('sessionDirectnessLevel'),
                    responses_json
                ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
        finally:
            conn.close()

    def save_company_profile(self, profile_data: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM company_profiles WHERE company_id = ?", (profile_data.get('company_id'),))
            existing_profile = cursor.fetchone()
            if existing_profile:
                cursor.execute("""
                    UPDATE company_profiles
                    SET company_name = ?, industry = ?, team_size = ?, primary_business = ?,
                        communication_style = ?, main_channels = ?, target_audience = ?,
                        generated_profile = ?, survey_data = ?
                    WHERE company_id = ?
                """, (
                    profile_data.get('company_name'),
                    profile_data.get('industry'),
                    profile_data.get('team_size'),
                    profile_data.get('primary_business'),
                    profile_data.get('communication_style'),
                    json.dumps(profile_data.get('main_channels', [])),
                    json.dumps(profile_data.get('target_audience', [])),
                    profile_data.get('generated_profile'),
                    json.dumps(profile_data.get('survey_data', {})),
                    profile_data.get('company_id')
                ))
            else:
                cursor.execute("""
                    INSERT INTO company_profiles (company_id, company_name, industry, team_size, primary_business,
                                           communication_style, main_channels, target_audience,
                                           generated_profile, survey_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_data.get('company_id'),
                    profile_data.get('company_name'),
                    profile_data.get('industry'),
                    profile_data.get('team_size'),
                    profile_data.get('primary_business'),
                    profile_data.get('communication_style'),
                    json.dumps(profile_data.get('main_channels', [])),
                    json.dumps(profile_data.get('target_audience', [])),
                    profile_data.get('generated_profile'),
                    json.dumps(profile_data.get('survey_data', {}))
                ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving company profile: {e}")
            return False
        finally:
            conn.close()

    def get_all_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_rating, selected_version FROM conversion_history WHERE user_id = ? AND user_rating IS NOT NULL", (user_id,))
        feedback = cursor.fetchall()
        conn.close()
        return [dict(row) for row in feedback]

    def update_conversion_feedback(self, feedback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE conversion_history
                SET user_rating = ?, selected_version = ?, feedback_text = ?
                WHERE id = ?
            """, (
                feedback_data.get('rating'),
                feedback_data.get('selectedVersion'),
                feedback_data.get('feedback_text'),
                feedback_data.get('conversionId')
            ))
            conn.commit()
            cursor.execute("SELECT * FROM conversion_history WHERE id = ?", (feedback_data.get('conversionId'),))
            updated_conversion = cursor.fetchone()
            if updated_conversion:
                return dict(updated_conversion)
            return None
        except Exception as e:
            logger.error(f"Error updating conversion feedback: {e}")
            return None
        finally:
            conn.close()

    def get_conversion_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversion_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return [dict(row) for row in history]
