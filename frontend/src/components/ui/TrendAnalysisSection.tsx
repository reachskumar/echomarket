import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

interface TrendAnalysisProps {
  summary: string;
  direction: "bullish" | "bearish" | "neutral";
  strength: "strong" | "moderate" | "weak";
  confidence: number;
  keyFactors: string[];
  timeframe: string;
  riskLevel: "low" | "medium" | "high";
}

export const TrendAnalysisSection: React.FC<TrendAnalysisProps> = ({
  summary,
  direction,
  strength,
  confidence,
  keyFactors,
  timeframe,
  riskLevel,
}) => {
  const directionColors = {
    bullish: "text-green-500",
    bearish: "text-red-500",
    neutral: "text-gray-500",
  };

  const riskColors = {
    low: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    high: "bg-red-100 text-red-700",
  };

  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-primary">
          Trend Analysis
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{summary}</p>

        <div className="flex flex-wrap gap-4 items-center text-sm">
          <span className={`${directionColors[direction]} font-semibold`}>
            Direction: {direction.toUpperCase()}
          </span>
          <span className="text-blue-500 font-semibold">
            Strength: {strength.toUpperCase()}
          </span>
          <span className="text-muted-foreground">
            Confidence: {confidence}%
          </span>
          <span className={`px-2 py-1 rounded ${riskColors[riskLevel]}`}>
            Risk: {riskLevel.toUpperCase()}
          </span>
          <span className="text-muted-foreground">
            Timeframe: {timeframe}
          </span>
        </div>

        <div>
          <p className="font-semibold text-sm text-foreground mb-2">
            Key Factors:
          </p>
          <ul className="list-disc list-inside text-sm space-y-1 text-muted-foreground">
            {keyFactors.map((factor, idx) => (
              <li key={idx}>{factor}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
