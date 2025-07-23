import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface PriceStatsProps {
  current: number;
  change: number;
  changePercent: number;
  symbol: string;
}

export const PriceStats = ({
  current,
  change,
  changePercent,
  symbol,
}: PriceStatsProps) => {
  const isPositive = change >= 0;
  const ChangeIcon = isPositive ? TrendingUp : TrendingDown;
  const changeColor = isPositive ? "text-emerald-500" : "text-red-500";

  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-primary">
          Price Overview – {symbol}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-bold text-foreground mb-2">
          ${current.toFixed(2)}
        </div>
        <div className={`flex items-center gap-1 text-lg font-medium ${changeColor}`}>
          <ChangeIcon size={18} />
          {isPositive ? "+" : ""}
          {change.toFixed(2)} ({isPositive ? "+" : ""}
          {changePercent.toFixed(2)}%)
        </div>
        <p className="text-sm text-muted-foreground mt-2">Last traded price</p>
      </CardContent>
    </Card>
  );
};
