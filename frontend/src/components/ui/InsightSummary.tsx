import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

interface InsightSummaryProps {
  summary: string;
}

const InsightSummary: React.FC<InsightSummaryProps> = ({ summary }) => {
  return (
    <Card className="w-full rounded-xl shadow-md border border-border bg-card">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-primary">
          Executive Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          {summary || "No insights available at this time."}
        </p>
      </CardContent>
    </Card>
  );
};

export default InsightSummary;
