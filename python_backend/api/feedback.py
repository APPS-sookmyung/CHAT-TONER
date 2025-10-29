from fastapi import APIRouter, Request, status
from api.v1.schemas.quality import UserFeedbackRequest as UserFeedback
from typing import Dict

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_and_learn_feedback(request: Request, feedback_data: UserFeedback) -> Dict[str, str]:
    """
    사용자로부터 피드백을 받아 세션에 저장
    """
    session = request.session

    # 세션에 사용자 선호도(preferences) 정보가 없으면 초기화
    if 'preferences' not in session:
        session['preferences'] = {
            "history": [],
            "learned_style": {
                "preferred_transformation_counts": {}
            }
        }

    # 받은 피드백을 기록(history)에 저장
    session['preferences']['history'].append(feedback_data.dict())

    # 선호 말투 학습 로직 (현재 스키마에 맞게 수정)
    # feedback_value를 기반으로 선호도 학습
    feedback_key = f"{feedback_data.feedback_type}_{feedback_data.feedback_value}"
    counts = session['preferences']['learned_style']['preferred_transformation_counts']
    counts[feedback_key] = counts.get(feedback_key, 0) + 1

    # 추가 메타데이터 저장
    session['preferences']['learned_style']['last_feedback'] = {
        'feedback_type': feedback_data.feedback_type,
        'feedback_value': feedback_data.feedback_value,
        'target_audience': feedback_data.target_audience,
        'context': feedback_data.context,
        'suggestion_category': feedback_data.suggestion_category
    }


    # 변경된 세션 데이터는 FastAPI가 자동으로 저장
    return {"message": "피드백이 성공적으로 반영되었습니다."}


@router.get("/preferences", response_model=Dict)
def get_user_preferences(request: Request):
    """
    현재 세션에 저장된 사용자 선호도 데이터를 반환합니다.
    (개발 및 말투 변환 적용 시 활용)
    """
    # 세션에 선호도 데이터가 없으면 빈 객체를 반환
    return request.session.get('preferences', {})