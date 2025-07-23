import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { TrendingUp, TrendingDown, Loader } from "lucide-react";

interface RecommendationProps {
  insight?: string;
  action?: string;
  confidence?: number;
  risk?: string;
  timeHorizon?: string;
  recommendationExplanation?: string;
}

const AIRecommendationCard: React.FC<RecommendationProps> = ({
  insight = "No insight available.",
  action = "Hold",
  confidence = 0,
  risk = "Unknown",
  timeHorizon = "N/A",
  recommendationExplanation = "No explanation provided.",
}) => {
  const badgeStyle =
    action.toLowerCase() === "buy"
      ? "bg-green-200 text-green-800"
      : action.toLowerCase() === "sell"
      ? "bg-red-200 text-red-800"
      : "bg-yellow-200 text-yellow-800";

  const icon =
    action.toLowerCase() === "buy" ? (
      <TrendingUp size={16} className="mr-1" />
    ) : action.toLowerCase() === "sell" ? (
      <TrendingDown size={16} className="mr-1" />
    ) : (
      <Loader size={16} className="mr-1" />
    );

  return (
    <Card className="rounded-xl shadow-md border border-border bg-card">
      <CardHeader className="pb-2 flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-primary">
          Investment Recommendation
        </CardTitle>
        <span
          className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${badgeStyle}`}
        >
          {icon}
          {action.toUpperCase()}
        </span>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          <strong>AI Insight:</strong> {insight}
        </div>

        <div className="text-sm text-accent">{recommendationExplanation}</div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-muted-foreground">Confidence</span>
            <div>{!isNaN(confidence) ? `${confidence}%` : "N/A"}</div>
          </div>
          <div>
            <span className="font-medium text-muted-foreground">Risk Level</span>
            <div>{risk}</div>
          </div>
          <div>
            <span className="font-medium text-muted-foreground">Time Horizon</span>
            <div>{timeHorizon}</div>
          </div>
          <div>
            <span className="font-medium text-muted-foreground">Action</span>
            <div>{action}</div>
          </div>
        </div>

        <p className="text-xs text-muted-foreground italic pt-2">
          ⚠️ This recommendation is AI-generated and not financial advice. Please consult your advisor.
        </p>
      </CardContent>
    </Card>
  );
};

export default AIRecommendationCard;
