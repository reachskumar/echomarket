import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

interface PriceData {
  date: string;
  price: number;
  volume?: number;
}

interface Props {
  data: PriceData[];
  symbol: string;
}

export const PriceTrendChart: React.FC<Props> = ({ data, symbol }) => {
  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-primary">
          Price Trend – Last 30 Days ({symbol})
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 pt-4">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
