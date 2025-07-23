import React from "react";
import SentimentScore from "@/components/ui/SentimentScore";
import { PriceStats } from "@/components/ui/PriceStats";

interface ExecutiveSummaryRowProps {
  sentimentScore: number;
  sentimentLabel: "Bullish" | "Bearish" | "Neutral";
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  analysisScore: number;
}

export const ExecutiveSummaryRow: React.FC<ExecutiveSummaryRowProps> = ({
  sentimentScore,
  sentimentLabel,
  currentPrice,
  priceChange,
  priceChangePercent,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
      <div className="min-h-[120px]">
        <SentimentScore score={sentimentScore} label={sentimentLabel} />
      </div>

      <div className="min-h-[120px]">
        <PriceStats
          current={currentPrice}
          change={priceChange}
          changePercent={priceChangePercent}
          symbol=""
        />
      </div>
    </div>
  );
};
