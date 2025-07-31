"""
Services 폴더 구조 및 모듈 확인 스크립트
"""

import sys
import os
from pathlib import Path
import importlib.util

def check_services_structure():
    """Services 폴더 구조와 모듈 상태 확인"""
    
    # 현재 파일 기준으로 경로 설정
    current_file = Path(__file__).resolve()
    python_backend = current_file.parents[2]  # python_backend 폴더
    services_path = python_backend / 'services'
    
    print("=" * 60)
    print("🔍 SERVICES 폴더 구조 확인")
    print("=" * 60)
    
    print(f"📂 Python Backend Path: {python_backend}")
    print(f"📂 Services Path: {services_path}")
    print(f"📂 Services 존재 여부: {services_path.exists()}")
    
    if not services_path.exists():
        print("❌ Services 폴더가 존재하지 않습니다!")
        return
    
    # sys.path에 추가
    sys.path.insert(0, str(python_backend))
    print(f"✅ sys.path에 추가됨: {python_backend}")
    
    print("\n" + "=" * 60)
    print("📋 SERVICES 폴더 내 파일 목록")
    print("=" * 60)
    
    # services 폴더 내 모든 파일 확인
    for item in sorted(services_path.iterdir()):
        if item.is_file():
            print(f"📄 {item.name}")
            if item.suffix == '.py':
                # Python 파일인 경우 기본 정보 확인
                try:
                    with open(item, 'r', encoding='utf-8') as f:
                        first_lines = f.readlines()[:10]
                        classes = [line.strip() for line in first_lines if line.strip().startswith('class ')]
                        functions = [line.strip() for line in first_lines if line.strip().startswith('def ')]
                        
                        if classes:
                            print(f"   🏗️  클래스: {', '.join(classes)}")
                        if functions:
                            print(f"   ⚙️  함수: {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''}")
                            
                except Exception as e:
                    print(f"   ❌ 파일 읽기 실패: {e}")
        elif item.is_dir():
            print(f"📁 {item.name}/")
    
    print("\n" + "=" * 60)
    print("🔧 모듈 IMPORT 테스트")
    print("=" * 60)
    
    # 각 모듈별 import 테스트
    modules_to_test = [
        'services',
        'services.base_service',
        'services.openai_services', 
        'services.openai_service',  # 오타 가능성 체크
        'services.prompt_engineering',
        'services.conversation_service',
    ]
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}: 성공")
            
            # 모듈 내 주요 클래스/함수 확인
            if hasattr(module, '__all__'):
                print(f"   📋 __all__: {module.__all__}")
            else:
                # 주요 클래스들 찾기
                attrs = [attr for attr in dir(module) 
                        if not attr.startswith('_') and attr[0].isupper()]
                if attrs:
                    print(f"   🏗️  클래스들: {', '.join(attrs[:5])}")
                    
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️  {module_name}: 기타 오류 - {e}")
    
    print("\n" + "=" * 60)
    print("🔍 파일명 세부 확인")
    print("=" * 60)
    
    # 파일명 정확성 체크
    expected_files = [
        '__init__.py',
        'base_service.py', 
        'openai_services.py',
        'prompt_engineering.py',
        'conversation_service.py'
    ]
    
    actual_files = [f.name for f in services_path.iterdir() if f.is_file()]
    
    for expected in expected_files:
        if expected in actual_files:
            print(f"✅ {expected}: 존재함")
        else:
            print(f"❌ {expected}: 없음")
            # 비슷한 이름 찾기
            similar = [f for f in actual_files if expected.replace('.py', '') in f.lower()]
            if similar:
                print(f"   🔍 비슷한 파일: {similar}")
    
    print(f"\n📋 실제 파일들: {actual_files}")
    
    print("\n" + "=" * 60)
    print("🐍 PYTHON PATH 확인")
    print("=" * 60)
    
    print("현재 sys.path:")
    for i, path in enumerate(sys.path[:10]):  # 처음 10개만
        print(f"{i+1:2d}. {path}")
    if len(sys.path) > 10:
        print(f"    ... 총 {len(sys.path)}개 경로")

if __name__ == "__main__":
    check_services_structure()