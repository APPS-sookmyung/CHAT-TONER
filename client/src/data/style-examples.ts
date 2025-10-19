export interface StyleExample {
  id: string;
  situation: string;
  options: {
    A: {
      text: string;
      style: 'direct' | 'gentle' | 'neutral';
      characteristics: string[];
    };
    B: {
      text: string;
      style: 'direct' | 'gentle' | 'neutral';
      characteristics: string[];
    };
    C: {
      text: string;
      style: 'direct' | 'gentle' | 'neutral';
      characteristics: string[];
    };
  };
}

export const styleExamples: StyleExample[] = [
  {
    id: "meeting_late",
    situation: "Apologizing for being late to a meeting",
    options: {
      A: {
        text: "I'm sorry for being late.",
        style: 'direct',
        characteristics: ['Concise', 'Direct', 'Formal']
      },
      B: {
        text: "I'm so sorry! I was late because of a traffic jam. Have you been waiting long?",
        style: 'gentle',
        characteristics: ['Detailed explanation', 'Emotional', 'Friendly']
      },
      C: {
        text: "I'm sorry. I was late due to a traffic jam.",
        style: 'neutral',
        characteristics: ['Moderate explanation', 'Neutral', 'Polite']
      }
    }
  },
  {
    id: "request_help",
    situation: "Asking a colleague for help",
    options: {
      A: {
        text: "Please help me with this.",
        style: 'direct',
        characteristics: ['Concise', 'Direct', 'Simple and clear']
      },
      B: {
        text: "If you have time, could you help me with this part? I'm not very familiar with it.",
        style: 'gentle',
        characteristics: ['Polite', 'Considerate', 'Humble']
      },
      C: {
        text: "I need help with this part. I would appreciate it if you could help me when you have time.",
        style: 'neutral',
        characteristics: ['Courteous', 'Clear', 'Professional']
      }
    }
  },
  {
    id: "disagree_opinion",
    situation: "Expressing a dissenting opinion when you have a different opinion",
    options: {
      A: {
        text: "I don't think so.",
        style: 'direct',
        characteristics: ['Honest', 'Direct', 'Concise']
      },
      B: {
        text: "What you said is good, but I think there might be a slightly different way. What do you think?",
        style: 'gentle',
        characteristics: ['Euphemistic', 'Considerate', 'Conversational']
      },
      C: {
        text: "That's a good opinion, but from a different perspective, we could also consider this method.",
        style: 'neutral',
        characteristics: ['Objective', 'Balanced', 'Logical']
      }
    }
  },
  {
    id: "express_gratitude",
    situation: "Expressing gratitude to a superior",
    options: {
      A: {
        text: "Thank you.",
        style: 'direct',
        characteristics: ['Concise', 'Formal', 'Clear']
      },
      B: {
        text: "Thank you so much for your help! Thanks to you, I was able to solve it well.",
        style: 'gentle',
        characteristics: ['Emotional', 'Specific', 'Warm']
      },
      C: {
        text: "Thank you for your help. Thanks to you, the work went smoothly.",
        style: 'neutral',
        characteristics: ['Polite', 'Specific', 'Professional']
      }
    }
  },
  {
    id: "give_feedback",
    situation: "Giving feedback to a subordinate",
    options: {
      A: {
        text: "This part needs to be revised.",
        style: 'direct',
        characteristics: ['Clear', 'Direct', 'Concise']
      },
      B: {
        text: "You did a good job overall, but I think it would be even better if you could supplement this part a little more. What do you think?",
        style: 'gentle',
        characteristics: ['Encouraging', 'Soft', 'Cooperative']
      },
      C: {
        text: "It was a good job. However, it seems that this part needs improvement.",
        style: 'neutral',
        characteristics: ['Balanced', 'Constructive', 'Objective']
      }
    }
  }
];

export function analyzeStylePreferences(choices: Record<string, 'A' | 'B' | 'C'>): {
  directness: number;
  formality: number;
  emotion: number;
  friendliness: number;
} {
  let directCount = 0;
  let gentleCount = 0;
  let neutralCount = 0;
  
  Object.values(choices).forEach(choice => {
    const example = styleExamples.find(ex => ex.id in choices);
    if (example) {
      const selectedOption = example.options[choice];
      switch (selectedOption.style) {
        case 'direct':
          directCount++;
          break;
        case 'gentle':
          gentleCount++;
          break;
        case 'neutral':
          neutralCount++;
          break;
      }
    }
  });
  
  const total = directCount + gentleCount + neutralCount;
  
  return {
    directness: total > 0 ? Math.round((directCount / total) * 10) : 5,
    formality: total > 0 ? Math.round(((directCount + neutralCount) / total) * 10) : 5,
    emotion: total > 0 ? Math.round((gentleCount / total) * 10) : 5,
    friendliness: total > 0 ? Math.round((gentleCount / total) * 10) : 5,
  };
}