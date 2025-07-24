// Export Actions Component
// 
// Provides buttons for users to download their stock analysis as PDF or CSV files.


import React from "react";
import { Button } from "@/components/ui/button";
import { FileText, Table } from "lucide-react";

interface ExportActionsProps {
  ticker: string;
  onExportPDF: () => void;
  onExportCSV: () => void;
  isLoading?: boolean;
}

const ExportActions: React.FC<ExportActionsProps> = ({
  ticker,
  onExportPDF,
  onExportCSV,
  isLoading = false,
}) => {
  return (
    <div className="flex flex-col sm:flex-row gap-3 p-4 bg-gray-50 rounded-lg border">
      <div className="flex-1">
        <h3 className="text-sm font-semibold text-gray-800 mb-1">
          Export Analysis
        </h3>
        <p className="text-xs text-gray-600">
          Save your {ticker} analysis for future reference or sharing
        </p>
      </div>
      
      <div className="flex gap-2">
        {/* PDF Export Button */}
        <Button
          onClick={onExportPDF}
          disabled={isLoading}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <FileText size={16} />
          <span className="hidden sm:inline">PDF Report</span>
          <span className="sm:hidden">PDF</span>
        </Button>

        {/* CSV Export Button */}
        <Button
          onClick={onExportCSV}
          disabled={isLoading}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <Table size={16} />
          <span className="hidden sm:inline">CSV Data</span>
          <span className="sm:hidden">CSV</span>
        </Button>
      </div>
    </div>
  );
};

export default ExportActions;
