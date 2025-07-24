// Trend Analysis Section Component
// Shows detailed trend analysis including direction, strength, and risk assessment.

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";

interface TrendAnalysisSectionProps {
  trend: {
    direction?: string;
    strength?: string;
    confidence?: number;
    risk?: string;
    timeframe?: string;
    keyFactors?: string[];
    summary?: string;
  };
}

export const TrendAnalysisSection: React.FC<TrendAnalysisSectionProps> = ({
  trend,
}) => {
  // Handle missing or incomplete trend data
  if (!trend || !trend.direction) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800">
            Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <Activity size={32} className="mx-auto mb-2 opacity-50" />
            <p>Trend analysis not available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Determine styling based on trend direction
  const isUptrend = trend.direction?.toLowerCase().includes("up");
  const isDowntrend = trend.direction?.toLowerCase().includes("down");
  
  const directionColor = isUptrend 
    ? "text-green-600" 
    : isDowntrend 
    ? "text-red-600" 
    : "text-gray-600";

  const DirectionIcon = isUptrend 
    ? TrendingUp 
    : isDowntrend 
    ? TrendingDown 
    : Activity;

  // Risk level styling
  const getRiskStyle = (risk: string) => {
    const riskLower = risk?.toLowerCase() || "";
    if (riskLower.includes("high")) {
      return "text-red-600 bg-red-50";
    } else if (riskLower.includes("medium")) {
      return "text-yellow-600 bg-yellow-50";
    } else {
      return "text-green-600 bg-green-50";
    }
  };

  const riskStyle = getRiskStyle(trend.risk || "");

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
          <DirectionIcon size={20} className={directionColor} />
          <span>Trend Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm text-gray-600">Direction:</span>
            <div className={`text-xl font-bold ${directionColor}`}>
              {trend.direction}
            </div>
          </div>
          
          <div className="text-right">
            <span className="text-sm text-gray-600">Strength:</span>
            <div className="text-lg font-semibold text-gray-800">
              {trend.strength || "N/A"}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {trend.confidence && (
            <div>
              <span className="text-sm text-gray-600">Confidence:</span>
              <div className="flex items-center space-x-2">
                <div className="text-lg font-semibold">
                  {Math.round(trend.confidence * 100)}%
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${trend.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          {trend.risk && (
            <div>
              <span className="text-sm text-gray-600">Risk Level:</span>
              <div className={`inline-block px-2 py-1 rounded text-sm font-medium ${riskStyle}`}>
                {trend.risk}
              </div>
            </div>
          )}
        </div>

      
        {trend.keyFactors && trend.keyFactors.length > 0 && (
          <div>
            <span className="text-sm font-semibold text-gray-700 mb-2 block">
              Key Factors:
            </span>
            <ul className="space-y-1 text-sm text-gray-600">
              {trend.keyFactors.map((factor, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

       
        {trend.summary && (
          <div className="pt-3 border-t border-gray-200">
            <span className="text-sm font-semibold text-gray-700 mb-2 block">
              Summary:
            </span>
            <p className="text-sm text-gray-600 leading-relaxed">
              {trend.summary}
            </p>
          </div>
        )}

        
        {trend.timeframe && (
          <div className="text-xs text-gray-500">
            Analysis timeframe: {trend.timeframe}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
