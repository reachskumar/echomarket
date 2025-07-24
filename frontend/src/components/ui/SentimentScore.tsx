// Sentiment Analysis Component
// 
// Shows the overall market sentiment about the stock based on recent news.

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus, AlertCircle } from "lucide-react";

interface SentimentScoreProps {
  sentiment: string;
  confidence: number;
}

const SentimentScore: React.FC<SentimentScoreProps> = ({
  sentiment,
  confidence,
}) => {
  // Determine what type of sentiment we're dealing with
  const isBullish = sentiment.toLowerCase().includes("bullish") || sentiment.toLowerCase().includes("positive");
  const isBearish = sentiment.toLowerCase().includes("bearish") || sentiment.toLowerCase().includes("negative");
  const isNeutral = sentiment.toLowerCase().includes("neutral") || (!isBullish && !isBearish);

  // Choose colors and icons based on sentiment
  const sentimentColor = isBullish 
    ? "text-green-600" 
    : isBearish 
    ? "text-red-600" 
    : "text-gray-600";

  const bgColor = isBullish 
    ? "bg-green-50" 
    : isBearish 
    ? "bg-red-50" 
    : "bg-gray-50";

  const borderColor = isBullish 
    ? "border-l-green-500" 
    : isBearish 
    ? "border-l-red-500" 
    : "border-l-gray-400";

  const SentimentIcon = isBullish 
    ? TrendingUp 
    : isBearish 
    ? TrendingDown 
    : Minus;

  // Convert confidence to percentage and determine if it's reliable
  const confidencePercent = Math.round(confidence * 100);
  const isHighConfidence = confidence >= 0.7;
  const isMediumConfidence = confidence >= 0.4;

  return (
    <Card className={`${bgColor} border-l-4 ${borderColor}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800">
          Market Sentiment
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between mb-4">
          <div className={`flex items-center space-x-2 ${sentimentColor}`}>
            <SentimentIcon size={24} />
            <span className="text-2xl font-bold capitalize">
              {sentiment}
            </span>
          </div>

          
          <div className="text-right">
            <div className="text-lg font-semibold text-gray-700">
              {confidencePercent}%
            </div>
            <div className="text-sm text-gray-500">Confidence</div>
          </div>
        </div>

        
        <div className="mb-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600">Confidence Level</span>
            <span className="text-xs text-gray-600">
              {isHighConfidence ? "High" : isMediumConfidence ? "Medium" : "Low"}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                isHighConfidence ? "bg-green-500" : isMediumConfidence ? "bg-yellow-500" : "bg-red-500"
              }`}
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
        </div>

        
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            {isBullish && "Recent news suggests positive outlook for this stock"}
            {isBearish && "Recent news suggests negative outlook for this stock"}
            {isNeutral && "Recent news shows mixed or neutral outlook"}
          </p>
          
          
          {!isMediumConfidence && (
            <div className="flex items-center mt-2 text-orange-600">
              <AlertCircle size={12} className="mr-1" />
              <span className="text-xs">
                Low confidence - consider additional research
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default SentimentScore;
