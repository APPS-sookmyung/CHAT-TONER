import type { ConversionContext } from "./types";

export const getContextLabel = (ctx: ConversionContext): string => {
  const labels: Record<ConversionContext, string> = {
    general: "General",
    report: "Report/Document",
    education: "Education/Explanation",
    social: "Social Media",
  };
  return labels[ctx];
};

export const copyToClipboard = async (text: string): Promise<void> => {
  await navigator.clipboard.writeText(text);
};
