import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface Props {
  current?: number;
  change?: number;
  changePercent?: number;
}

export const CurrentPriceCard: React.FC<Props> = ({
  current = 0,
  change = 0,
  changePercent = 0,
}) => {
  const isPositive = change >= 0;
  const ChangeIcon = isPositive ? TrendingUp : TrendingDown;
  const changeColor = isPositive ? "text-green-600" : "text-red-600";

  const safeCurrent = !isNaN(current) ? current : 0;
  const safeChange = !isNaN(change) ? change : 0;
  const safeChangePercent = !isNaN(changePercent) ? changePercent : 0;

  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Current Price
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-3xl font-bold">${safeCurrent.toFixed(2)}</div>
        <div className={`flex items-center gap-1 text-sm font-medium ${changeColor}`}>
          <ChangeIcon size={16} />
          {isPositive ? "+" : "-"}${Math.abs(safeChange).toFixed(2)} (
          {Math.abs(safeChangePercent).toFixed(2)}%)
        </div>
      </CardContent>
    </Card>
  );
};
