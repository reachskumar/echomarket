// Market News Component
// Displays recent news articles related to the stock being analyzed.

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Newspaper } from "lucide-react";

interface NewsItem {
  title: string;
  snippet: string;
  url: string;
}

interface MarketNewsProps {
  news: NewsItem[];
  ticker?: string;
}

export const MarketNews: React.FC<MarketNewsProps> = ({
  news,
  ticker,
}) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
          <Newspaper size={20} className="text-blue-600" />
          <span>
            Recent News {ticker && `(${ticker})`}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {news && news.length > 0 ? (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              Found {news.length} recent article{news.length !== 1 ? 's' : ''}
            </div>

           
            {news.slice(0, 8).map((article, index) => (
              <div 
                key={index} 
                className="border-l-4 border-blue-200 pl-4 py-2 hover:bg-gray-50 transition-colors"
              >
                <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
                  {article.title}
                </h4>
                
                {article.snippet && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                    {article.snippet}
                  </p>
                )}
                
                {article.url && (
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <span>Read full article</span>
                    <ExternalLink size={14} className="ml-1" />
                  </a>
                )}
              </div>
            ))}

            {news.length > 8 && (
              <div className="text-sm text-gray-500 text-center pt-4 border-t">
                And {news.length - 8} more article{news.length - 8 !== 1 ? 's' : ''}...
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Newspaper size={32} className="mx-auto mb-2 opacity-50" />
            <p>No recent news articles found</p>
            <p className="text-xs mt-1">
              We couldn't find recent news for this stock
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
