// Executive Summary Row Component
// Displays key metrics from the stock analysis in a clean, organized row format.


import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Shield, AlertTriangle } from "lucide-react";

interface ExecutiveSummaryRowProps {
  price?: number;
  sentiment?: string;
  recommendation?: string;
  confidence?: number;
  riskLevel?: string;
}

export const ExecutiveSummaryRow: React.FC<ExecutiveSummaryRowProps> = ({
  price,
  sentiment,
  recommendation,
  confidence,
  riskLevel,
}) => {
  // Helper function to get appropriate styling for different values
  const getSentimentColor = (sentiment: string) => {
    const sentimentLower = sentiment?.toLowerCase() || "";
    if (sentimentLower.includes("bullish") || sentimentLower.includes("positive")) {
      return "text-green-600";
    } else if (sentimentLower.includes("bearish") || sentimentLower.includes("negative")) {
      return "text-red-600";
    }
    return "text-gray-600";
  };

  const getRecommendationIcon = (rec: string) => {
    const recLower = rec?.toLowerCase() || "";
    if (recLower === "buy") return TrendingUp;
    if (recLower === "sell") return TrendingDown;
    return Shield;
  };

  const getRecommendationColor = (rec: string) => {
    const recLower = rec?.toLowerCase() || "";
    if (recLower === "buy") return "text-green-600";
    if (recLower === "sell") return "text-red-600";
    return "text-blue-600";
  };

  const RecommendationIcon = recommendation ? getRecommendationIcon(recommendation) : Shield;

  return (
    <Card className="mb-6">
      <CardContent className="pt-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          {/* Current Price */}
          <div className="space-y-1">
            <div className="text-sm text-gray-600 font-medium">Price</div>
            <div className="text-xl font-bold text-gray-900">
              {(typeof price === 'number' && price > 0) ? `$${price.toFixed(2)}` : "N/A"}
            </div>
          </div>

          {/* Sentiment */}
          <div className="space-y-1">
            <div className="text-sm text-gray-600 font-medium">Sentiment</div>
            <div className={`text-lg font-semibold ${getSentimentColor(sentiment || "")}`}>
              {sentiment || "N/A"}
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="space-y-1">
            <div className="text-sm text-gray-600 font-medium">Recommendation</div>
            <div className={`flex items-center justify-center space-x-1 text-lg font-semibold ${getRecommendationColor(recommendation || "")}`}>
              <RecommendationIcon size={18} />
              <span>{recommendation || "N/A"}</span>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="space-y-1">
            <div className="text-sm text-gray-600 font-medium">Confidence</div>
            <div className="text-lg font-semibold text-gray-900">
              {(typeof confidence === 'number' && confidence >= 0) ? `${Math.round(confidence * 100)}%` : "N/A"}
            </div>
          </div>

          {/* Risk Level */}
          <div className="space-y-1">
            <div className="text-sm text-gray-600 font-medium">Risk Level</div>
            <div className="flex items-center justify-center space-x-1">
              {riskLevel?.toLowerCase() === "high" && (
                <AlertTriangle size={16} className="text-red-500" />
              )}
              <span className={`text-lg font-semibold ${
                riskLevel?.toLowerCase() === "high" ? "text-red-600" :
                riskLevel?.toLowerCase() === "medium" ? "text-yellow-600" :
                "text-green-600"
              }`}>
                {riskLevel || "N/A"}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
