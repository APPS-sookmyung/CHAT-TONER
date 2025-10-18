export const PATH = {
  // --- 1. 정적 경로 (주소가 고정된 페이지) ---

  /**
   * @description 랜딩 페이지
   * @path /
   */
  HOME: "/",

  /**
   * @description 기능 선택 페이지
   * @path /choice
   */
  CHOICE: "/choice",

  /**
   * @description 스타일 변환 페이지
   * @path /transform-style
   */
  TRANSFORM_STYLE: "/transform-style",

  /**
   * @description 품질 분석 페이지
   * @path /analyze-quality
   */
  ANALYZE_QUALITY: "/analyze-quality",

  // --- 2. 동적 경로 (주소에 변수가 포함된 페이지) ---

  /**
   * @description 설문조사 페이지
   * @param step - 설문 단계 (1, 2, ...)
   * @path /survey/:step
   * @returns /survey/[step]
   */
  SURVEY: (step: number | string) => `/survey/${step}`,
};
