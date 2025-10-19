import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Settings, Filter, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UserNegativePreferences {
  rhetoricLevel: "strict" | "moderate" | "lenient";
  repetitionTolerance: "strict" | "moderate" | "lenient";
  punctuationStyle: "minimal" | "standard" | "verbose";
  contentFocus: "content" | "balanced" | "format";
  bulletPreference: "avoid" | "minimal" | "prefer";
  emoticonPolicy: "none" | "minimal" | "contextual" | "frequent";
}

interface NegativePromptSettingsProps {
  userId: string;
  onSave?: (preferences: UserNegativePreferences) => void;
}

const defaultPreferences: UserNegativePreferences = {
  rhetoricLevel: "moderate",
  repetitionTolerance: "moderate",
  punctuationStyle: "standard",
  contentFocus: "balanced",
  bulletPreference: "minimal",
  emoticonPolicy: "contextual",
};

export function NegativePromptSettings({
  userId,
  onSave,
}: NegativePromptSettingsProps) {
  const [preferences, setPreferences] =
    useState<UserNegativePreferences>(defaultPreferences);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // Load saved settings on component mount
  useEffect(() => {
    const savedPreferences = localStorage.getItem(
      `negative-preferences-${userId}`
    );
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        setPreferences({ ...defaultPreferences, ...parsed });
      } catch (error) {
        console.error("Failed to load settings:", error);
      }
    }
  }, [userId]);

  const rhetoricOptions = [
    { value: "strict", label: "Strict", description: "Prohibit all exaggerated expressions" },
    { value: "moderate", label: "Moderate", description: "Moderate level of expression" },
    { value: "lenient", label: "Lenient", description: "Allow natural expressions" },
  ];

  const repetitionOptions = [
    { value: "strict", label: "Strict", description: "Completely prohibit repeated expressions" },
    { value: "moderate", label: "Moderate", description: "Allow only when necessary" },
    { value: "lenient", label: "Lenient", description: "Allow natural repetition" },
  ];

  const punctuationOptions = [
    { value: "minimal", label: "Minimal", description: "Only necessary commas" },
    { value: "standard", label: "Standard", description: "General use" },
    { value: "verbose", label: "Verbose", description: "Rich use of commas" },
  ];

  const contentFocusOptions = [
    { value: "content", label: "Content-focused", description: "Prioritize core content" },
    { value: "balanced", label: "Balanced", description: "Harmony between content and format" },
    { value: "format", label: "Format-focused", description: "Prioritize systematic composition" },
  ];

  const bulletOptions = [
    { value: "avoid", label: "Avoid", description: "Do not use bullet points" },
    { value: "minimal", label: "Minimal", description: "Use only when necessary" },
    { value: "prefer", label: "Prefer", description: "Active use" },
  ];

  const emoticonOptions = [
    { value: "none", label: "None", description: "Completely prohibit emoticons" },
    { value: "minimal", label: "Minimal", description: "Only basic ones" },
    { value: "contextual", label: "Contextual", description: "According to context" },
    { value: "frequent", label: "Frequent", description: "Frequent use" },
  ];

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Save to localStorage
      localStorage.setItem(
        `negative-preferences-${userId}`,
        JSON.stringify(preferences)
      );

      // Show success toast
      toast({
        title: "Settings saved",
        description: "Negative prompt preferences have been saved.",
      });

      onSave?.(preferences);
    } catch (error) {
      toast({
        title: "Save failed",
        description: "An error occurred while saving settings.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const updatePreference = <K extends keyof UserNegativePreferences>(
    key: K,
    value: UserNegativePreferences[K]
  ) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5" />
          <CardTitle>Negative Prompt Settings</CardTitle>
        </div>
        <CardDescription>
          Customize the expressions you want to exclude when converting text. These settings apply to all text conversions.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Rhetoric settings */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Label className="text-base font-medium">Rhetoric Limit</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Set the extent to which exaggerated modifiers such as "amazing", "great", and "excellent" are allowed.
          </p>
          <Select
            value={preferences.rhetoricLevel}
            onValueChange={(value: "strict" | "moderate" | "lenient") =>
              updatePreference("rhetoricLevel", value)
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {rhetoricOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Repetition expression settings */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline">Repeat</Badge>
            <Label className="text-base font-medium">Repetition Limit</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Restricts the repeated use of similar words such as "and also" and "as for ~".
          </p>
          <Select
            value={preferences.repetitionTolerance}
            onValueChange={(value: "strict" | "moderate" | "lenient") =>
              updatePreference("repetitionTolerance", value)
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {repetitionOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Comma usage style */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Label className="text-base font-medium">Comma Usage Style</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Sets the extent to which commas are used in a sentence.
          </p>
          <Select
            value={preferences.punctuationStyle}
            onValueChange={(value: "minimal" | "standard" | "verbose") =>
              updatePreference("punctuationStyle", value)
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {punctuationOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Content vs format priority */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Label className="text-base font-medium">
              Content vs. Format Priority
            </Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Set whether to prioritize content or format when converting text.
          </p>
          <Select
            value={preferences.contentFocus}
            onValueChange={(value: "content" | "balanced" | "format") =>
              updatePreference("contentFocus", value)
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {contentFocusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Bullet point usage */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Label className="text-base font-medium">Bullet Point Usage</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Sets the use of bullet points such as "•", "-", "1.".
          </p>
          <Select
            value={preferences.bulletPreference}
            onValueChange={(value: "avoid" | "minimal" | "prefer") =>
              updatePreference("bulletPreference", value)
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {bulletOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Emoticon policy */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline">Positive</Badge>
            <Label className="text-base font-medium">Emoticon Usage Policy</Label>
          </div>
          <p className="text-sm text-muted-foreground">
            Sets the extent to which emoticons are allowed in the text.
          </p>
          <Select
            value={preferences.emoticonPolicy}
            onValueChange={(
              value: "none" | "minimal" | "contextual" | "frequent"
            ) => updatePreference("emoticonPolicy", value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {emoticonOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Save button */}
        <div className="flex justify-end gap-3">
          <Button
            onClick={handleSave}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            {isLoading ? "Saving..." : "Save Settings"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
