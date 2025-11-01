export const PATH = {
  // --- 1st half existing paths ---
  /**
   * @description landing page
   * @path /
   */
  HOME: "/",

  /**
   * @description feature selection page
   * @path /choice
   */
  CHOICE: "/choice",

  /**
   * @description style transformation page
   * @path /transform-style
   */
  TRANSFORM_STYLE: "/transform-style",

  /**
   * @description quality analysis page
   * @path /analyze-quality
   */
  ANALYZE_QUALITY: "/analyze-quality",

  // --- 2nd half new paths ---

  /**
   * @description survey page
   * @param step - survey step (1, 2, ...)
   * @path /survey/:step
   * @returns /survey/[step]
   */
  SURVEY: (step: number | string) => `/survey/${step}`,

  RESULTS: "/results",

  UPLOAD: "/upload",

  COMPANY_PROFILE: (companyId: string) => `/company-profile/${companyId}`,

  COMPANY_SURVEY: "/company-survey",
};
