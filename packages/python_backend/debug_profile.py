#!/usr/bin/env python3
"""
프로필 저장 디버깅 스크립트
"""

import sys
import traceback
from database.storage import DatabaseStorage

def test_profile_save():
    """프로필 저장 테스트"""
    try:
        print("데이터베이스 스토리지 초기화...")
        storage = DatabaseStorage()
        
        # 테스트 데이터
        user_id = "test-uuid-12345"
        profile_data = {
            'baseFormalityLevel': 3,
            'baseFriendlinessLevel': 3,
            'baseEmotionLevel': 3,
            'baseDirectnessLevel': 3
        }
        
        print(f"프로필 저장 시도: user_id={user_id}")
        print(f"프로필 데이터: {profile_data}")
        
        # 프로필 저장 시도
        result = storage.save_user_profile(user_id, profile_data)
        
        print(f"저장 결과: {result}")
        
        if result:
            print("Profile saved successfully!")
            
            # 저장된 프로필 조회해보기
            print("\n저장된 프로필 조회 중...")
            saved_profile = storage.get_user_profile(user_id)
            print(f"조회된 프로필: {saved_profile}")
        else:
            print("Failed to save profile")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_profile_save()