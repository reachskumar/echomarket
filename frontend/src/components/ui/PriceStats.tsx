// Price Statistics Component
// Displays the current stock price along with recent price changes.

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface PriceStatsProps {
  symbol: string;
  price: number;
  priceChange: number;
  priceChangePercent: number;
}

export const PriceStats: React.FC<PriceStatsProps> = ({
  symbol,
  price,
  priceChange,
  priceChangePercent,
}) => {
  // Figure out if the price went up, down, or stayed the same
  const isPositive = priceChange > 0;
  const isNegative = priceChange < 0;
  const isNeutral = priceChange === 0;

  // Choose appropriate colors and icons based on price movement
  const trendColor = isPositive 
    ? "text-green-600" 
    : isNegative 
    ? "text-red-600" 
    : "text-gray-500";

  const bgColor = isPositive 
    ? "bg-green-50" 
    : isNegative 
    ? "bg-red-50" 
    : "bg-gray-50";

  const TrendIcon = isPositive 
    ? TrendingUp 
    : isNegative 
    ? TrendingDown 
    : Minus;

  return (
    <Card className={`${bgColor} border-l-4 ${isPositive ? 'border-l-green-500' : isNegative ? 'border-l-red-500' : 'border-l-gray-400'}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800">
          {symbol} Price
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          {/* Current price - the main number */}
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-gray-900">
              ${price.toFixed(2)}
            </span>
            <span className="text-sm text-gray-500">Current Price</span>
          </div>

          {/* Price change information */}
          <div className={`flex items-center space-x-2 ${trendColor}`}>
            <TrendIcon size={20} />
            <div className="text-right">
              <div className="font-semibold">
                {isPositive ? "+" : ""}{priceChange.toFixed(2)}
              </div>
              <div className="text-sm">
                ({isPositive ? "+" : ""}{priceChangePercent.toFixed(2)}%)
              </div>
            </div>
          </div>
        </div>

        {/* explanation of what the numbers mean */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            {isPositive && "Stock price increased from previous trading day"}
            {isNegative && "Stock price decreased from previous trading day"}
            {isNeutral && "Stock price unchanged from previous trading day"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
