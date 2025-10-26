import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Wand2, CheckCircle, ArrowRight } from "lucide-react";

interface ModeSelectorProps {
  onModeSelect: (mode: "transform" | "validate") => void;
}

export default function ModeSelector({ onModeSelect }: ModeSelectorProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          Which feature would you like to use?
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Please select the right tool for your purpose
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Style Transform Mode */}
        <Card
          className="relative hover:shadow-lg transition-all duration-200 cursor-pointer group"
          onClick={() => onModeSelect("transform")}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Wand2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-xl">Style Transformation</CardTitle>
                <CardDescription className="text-sm text-gray-500">
                  When you want to change the tone or style of your speech
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Transforms the tone or style of already written text to suit the situation.
            </p>

            <div className="space-y-2">
              <h4 className="font-medium text-sm">Use in cases like these:</h4>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• When you want to change a casual message to a polite one</li>
                <li>• When you want to make a stiff document more friendly</li>
                <li>• When you want to adjust your tone to the situation</li>
              </ul>
            </div>

            <Button
              className="w-full bg-blue-600 hover:bg-blue-700 group-hover:bg-blue-700 transition-colors text-white"
              onClick={(e) => {
                e.stopPropagation();
                onModeSelect("transform");
              }}
            >
              Transform Style
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Quality Validation Mode */}
        <Card
          className="relative hover:shadow-lg transition-all duration-200 cursor-pointer group"
          onClick={() => onModeSelect("validate")}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <CardTitle className="text-xl">Quality Validation</CardTitle>
                <CardDescription className="text-sm text-gray-500">
                  When you want to check if the completed text is appropriate
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Analyzes whether the completed text is appropriate for the context and suggests improvements.
            </p>

            <div className="space-y-2">
              <h4 className="font-medium text-sm">Use in cases like these:</h4>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• When you want to check the appropriateness of a report or official document</li>
                <li>• When you want to check spelling or grammar</li>
                <li>• When you want to improve with better expressions</li>
              </ul>
            </div>

            <Button
              className="w-full bg-green-600 hover:bg-green-700 group-hover:bg-green-700 transition-colors text-white"
              onClick={(e) => {
                e.stopPropagation();
                onModeSelect("validate");
              }}
            >
              Validate Quality
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="bg-blue-50 dark:bg-blue-950 p-6 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className="text-blue-600 dark:text-blue-400 mt-1"></div>
          <div>
            <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              Which tool should I choose?
            </h3>
            <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <p>
                <strong>Style Transformation:</strong> When the content is good but you only want to change the tone
              </p>
              <p>
                <strong>Quality Validation:</strong> When you want to check and improve the content itself
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
