import { useState, useEffect } from "react";

const THINKING_MESSAGES = [
  "에이전트가 생각하고 있어요",
  "더 좋은 답을 위해 고민 중이에요",
  "문맥을 분석하고 있습니다",
  "최적의 스타일을 찾는 중이에요",
  "잠시만 기다려 주세요",
];

/**
 * Hook to cycle through thinking messages when a loading state is active.
 * 
 * @param isLoading Whether the thinking state is active
 * @param intervalMs Interval between message changes in milliseconds
 * @returns The current thinking message
 */
export const useThinkingMessage = (isLoading: boolean, intervalMs: number = 2000) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isLoading) {
      interval = setInterval(() => {
        setIndex((prevIndex) => (prevIndex + 1) % THINKING_MESSAGES.length);
      }, intervalMs);
    } else {
      setIndex(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoading, intervalMs]);

  return THINKING_MESSAGES[index];
};
