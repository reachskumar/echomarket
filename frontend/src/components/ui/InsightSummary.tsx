// Insight Summary Component
// Displays the final AI-generated summary

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText } from "lucide-react";

interface InsightSummaryProps {
  summary: string;
  ticker?: string;
}

const InsightSummary: React.FC<InsightSummaryProps> = ({
  summary,
  ticker,
}) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
          <FileText size={20} className="text-blue-600" />
          <span>
            {ticker ? `${ticker} Analysis Summary` : "Analysis Summary"}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {summary ? (
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {summary}
            </p>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <FileText size={32} className="mx-auto mb-2 opacity-50" />
            <p>Summary not yet available</p>
            <p className="text-xs mt-1">
              Complete the analysis to see a comprehensive summary
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InsightSummary;
