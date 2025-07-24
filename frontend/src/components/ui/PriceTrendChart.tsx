// Price Trend Chart Component
// 
// Displays a visual chart of recent price movements for the stock.

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

interface PriceTrendChartProps {
  symbol: string;
  prices: Record<string, number>;
  currentPrice: number;
}

export const PriceTrendChart: React.FC<PriceTrendChartProps> = ({
  symbol,
  prices,
  currentPrice,
}) => {
  // Convert price data to chart-friendly format
  const priceData = Object.entries(prices)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, price]) => ({ date, price }));

  // Determine overall trend direction
  const firstPrice = priceData[0]?.price || currentPrice;
  const lastPrice = priceData[priceData.length - 1]?.price || currentPrice;
  const isUptrend = lastPrice > firstPrice;
  const isDowntrend = lastPrice < firstPrice;
  
  const trendColor = isUptrend ? "text-green-600" : isDowntrend ? "text-red-600" : "text-gray-600";
  const TrendIcon = isUptrend ? TrendingUp : isDowntrend ? TrendingDown : Minus;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
          <TrendIcon size={20} className={trendColor} />
          <span>{symbol} Price Trend</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {priceData.length > 0 ? (
          <div className="space-y-3">
            <div className="text-sm text-gray-600">
              Recent price movement ({priceData.length} data point{priceData.length !== 1 ? 's' : ''}):
            </div>
            <div style={{ width: "100%", height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} domain={[dataMin => Math.floor(dataMin * 0.98), dataMax => Math.ceil(dataMax * 1.02)]} />
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                  <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className={`text-sm font-medium ${trendColor}`}>
              {isUptrend && "📈 Upward trend"}
              {isDowntrend && "📉 Downward trend"}
              {!isUptrend && !isDowntrend && "➡️ Sideways movement"}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No price history available for chart</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
