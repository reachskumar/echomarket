import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

interface AnalysisScoreProps {
  score?: number;
  label?: string;
}

const AnalysisScore: React.FC<AnalysisScoreProps> = ({
  score = 0,
  label = "Market Sentiment Score",
}) => {
  const safeScore = isNaN(score) ? 0 : Math.max(0, Math.min(score, 100));

  const getColor = () => {
    if (safeScore >= 70) return "bg-green-500";
    if (safeScore >= 40) return "bg-yellow-400";
    return "bg-red-500";
  };

  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-bold text-foreground">{safeScore}/100</div>
        <div className="w-full bg-muted h-2 rounded-full mt-3">
          <div
            className={`${getColor()} h-2 rounded-full transition-all duration-500`}
            style={{ width: `${safeScore}%` }}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisScore;
