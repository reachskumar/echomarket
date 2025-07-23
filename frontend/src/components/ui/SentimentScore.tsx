import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

interface SentimentScoreProps {
  score: number;
  label: "Bullish" | "Bearish" | "Neutral";
}

const SentimentScore: React.FC<SentimentScoreProps> = ({ score, label }) => {
  const labelClass =
    label === "Bullish"
      ? "bg-green-200 text-green-700"
      : label === "Bearish"
      ? "bg-red-200 text-red-700"
      : "bg-gray-200 text-gray-700";

  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Market Sentiment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold flex items-center justify-between mt-2">
          <span>{score}%</span>
          <span className={`text-sm px-2 py-1 rounded ${labelClass}`}>
            {label}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

export default SentimentScore;
