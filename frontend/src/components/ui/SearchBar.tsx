import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

type SearchBarProps = {
  symbol: string;
  onSymbolChange: (value: string) => void;
  onAnalyze: () => void;
  loading?: boolean;
};

const SearchBar: React.FC<SearchBarProps> = ({
  symbol,
  onSymbolChange,
  onAnalyze,
  loading = false,
}) => {
  return (
    <div className="w-full flex flex-col sm:flex-row gap-4 items-center justify-center mt-10 px-4">
      <Input
        type="text"
        value={symbol}
        onChange={(e) => {
          console.log("💡 Triggering onSymbolChange with:", e.target.value);
          if (typeof onSymbolChange === "function") {
            onSymbolChange(e.target.value);
          } else {
            console.error("❌ onSymbolChange is NOT a function:", onSymbolChange);
          }
        }}
        placeholder="Enter ticker (e.g., AAPL, INFY)"
        className="sm:w-96"
      />
      <Button
        onClick={() => {
          console.log("💥 Analyze button clicked");
          if (typeof onAnalyze === "function") {
            onAnalyze();
          } else {
            console.error("❌ onAnalyze is NOT a function:", onAnalyze);
          }
        }}
        disabled={loading}
        variant="default"
        className="sm:w-auto w-full flex items-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin h-4 w-4" />
            Analyzing...
          </>
        ) : (
          "Analyze"
        )}
      </Button>
    </div>
  );
};

export default SearchBar;
