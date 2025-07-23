import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface NewsItem {
  title: string;
  snippet: string;
  link: string;
  source: string;
  publishedAt: string;
  sentiment?: "positive" | "neutral" | "negative";
}

interface MarketNewsProps {
  news: NewsItem[];
}

const sentimentColor = {
  positive: "bg-green-100 text-green-800",
  negative: "bg-red-100 text-red-800",
  neutral: "bg-gray-100 text-gray-800",
};

export const MarketNews = ({ news }: MarketNewsProps) => {
  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-primary">
          Market News
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {news.map((item, index) => (
          <div
            key={index}
            className="border border-border rounded-md p-4 hover:shadow-sm transition duration-200"
          >
            <div className="flex justify-between items-start mb-1 gap-2">
              <div className="flex flex-col">
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base font-semibold text-primary hover:underline"
                >
                  {item.title}
                </a>
                <p className="text-sm text-muted-foreground mt-1">{item.snippet}</p>
              </div>
              <div className="text-right space-y-1 text-xs text-muted-foreground">
                <div>{new Date(item.publishedAt).toLocaleDateString()}</div>
                <div>{item.source}</div>
                {item.sentiment && (
                  <div
                    className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${sentimentColor[item.sentiment]}`}
                  >
                    {item.sentiment}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
