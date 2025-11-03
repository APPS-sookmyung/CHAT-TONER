"""
PDF Summarization Service
PDF 문서의 내용을 추출하고 요약하는 서비스
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pypdf
from services.openai_services import OpenAIService

logger = logging.getLogger('chattoner.pdf_summary')

class PDFSummaryService:
    """PDF 문서 요약 서비스"""

    def __init__(self, openai_service: OpenAIService):
        """
        서비스 초기화

        Args:
            openai_service: OpenAI 서비스 인스턴스
        """
        self.openai_service = openai_service
        logger.info("PDFSummaryService 초기화 완료")

    def _extract_pdf_text(self, file_path: Path) -> str:
        """PDF 파일에서 텍스트를 추출합니다."""
        try:
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            logger.info(f"PDF 파일 텍스트 추출 완료: {file_path.name}, {len(text)} 자 추출")
            return text
        except Exception as e:
            logger.error(f"PDF 파일 텍스트 추출 중 오류 발생 ({file_path.name}): {e}")
            raise ValueError(f"PDF 파일 처리 실패: {file_path.name}") from e

    async def summarize_pdf_by_path(self, file_path: str, summary_type: str = "brief") -> Dict[str, Any]:
        """
        파일 경로를 받아 PDF를 요약합니다.

        Args:
            file_path: PDF 파일의 경로
            summary_type: 요약 유형 ("brief", "detailed", "bullet_points")

        Returns:
            요약 결과를 담은 딕셔너리
        """
        try:
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                return {"success": False, "error": f"파일을 찾을 수 없습니다: {file_path}"}

            if pdf_path.suffix.lower() != ".pdf":
                return {"success": False, "error": "PDF 파일만 지원됩니다"}

            # PDF 텍스트 추출
            document_text = self._extract_pdf_text(pdf_path)
            if not document_text.strip():
                return {"success": False, "error": "문서에서 텍스트를 추출할 수 없습니다"}

            # 요약 생성
            summary = await self._generate_summary(document_text, summary_type)

            return {
                "success": True,
                "file_name": pdf_path.name,
                "summary": summary,
                "summary_type": summary_type,
                "original_length": len(document_text),
                "summary_length": len(summary)
            }

        except Exception as e:
            logger.error(f"PDF 요약 생성 중 오류 발생: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def summarize_pdf_text(self, text: str, summary_type: str = "brief") -> Dict[str, Any]:
        """
        이미 추출된 텍스트를 요약합니다.

        Args:
            text: 요약할 텍스트
            summary_type: 요약 유형 ("brief", "detailed", "bullet_points")

        Returns:
            요약 결과를 담은 딕셔너리
        """
        try:
            if not text.strip():
                return {"success": False, "error": "요약할 텍스트가 비어있습니다"}

            # 요약 생성
            summary = await self._generate_summary(text, summary_type)

            return {
                "success": True,
                "summary": summary,
                "summary_type": summary_type,
                "original_length": len(text),
                "summary_length": len(summary)
            }

        except Exception as e:
            logger.error(f"텍스트 요약 생성 중 오류 발생: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _generate_summary(self, text: str, summary_type: str) -> str:
        """
        텍스트 요약을 생성합니다.

        Args:
            text: 요약할 텍스트
            summary_type: 요약 유형

        Returns:
            생성된 요약 텍스트
        """
        # 요약 유형별 프롬프트 설정
        if summary_type == "brief":
            system_prompt = (
                "당신은 문서 요약 전문가입니다. 주어진 텍스트를 2-3문장으로 간결하게 요약하세요. "
                "핵심 내용과 주요 포인트만 포함하고, 한국어로 응답하세요."
            )
            max_tokens = 300
        elif summary_type == "detailed":
            system_prompt = (
                "당신은 문서 요약 전문가입니다. 주어진 텍스트를 상세히 요약하세요. "
                "주요 섹션별로 구분하여 설명하고, 중요한 내용을 놓치지 않도록 하세요. "
                "한국어로 응답하세요."
            )
            max_tokens = 800
        elif summary_type == "bullet_points":
            system_prompt = (
                "당신은 문서 요약 전문가입니다. 주어진 텍스트의 핵심 내용을 "
                "불렛 포인트(•) 형식으로 정리하세요. 각 포인트는 한 줄로 간결하게 작성하고, "
                "한국어로 응답하세요."
            )
            max_tokens = 500
        else:
            # 기본값: brief
            system_prompt = (
                "당신은 문서 요약 전문가입니다. 주어진 텍스트를 2-3문장으로 간결하게 요약하세요. "
                "핵심 내용과 주요 포인트만 포함하고, 한국어로 응답하세요."
            )
            max_tokens = 300

        # 텍스트가 너무 길면 일부만 사용 (토큰 한계 고려)
        if len(text) > 8000:  # 대략적인 토큰 한계 고려
            logger.warning(f"텍스트가 너무 길어 첫 8000자만 사용합니다: {len(text)} -> 8000")
            text = text[:8000] + "..."

        user_prompt = f"다음 텍스트를 요약해주세요:\n\n{text}"

        try:
            summary = await self.openai_service.generate_text(
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.3,
                max_tokens=max_tokens
            )
            logger.info(f"{summary_type} 요약 생성 완료: {len(summary)}자")
            return summary

        except Exception as e:
            logger.error(f"요약 생성 실패: {e}")
            raise RuntimeError(f"요약 생성 중 오류 발생: {str(e)}")


def get_pdf_summary_service(openai_service: OpenAIService) -> PDFSummaryService:
    """PDF 요약 서비스 팩토리 함수"""
    return PDFSummaryService(openai_service)