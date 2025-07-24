// Search Bar Component
// Input field where users can type company names or ticker symbols.

import React from "react";
import { useRef, useEffect } from "react";
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
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus the input when component loads and after analysis finishes
  useEffect(() => {
    if (inputRef.current && !loading) {
      inputRef.current.focus();
    }
  }, [loading]);

  return (
    <div className="w-full flex flex-col sm:flex-row gap-4 items-center justify-center mt-10 px-4">
      <Input
        ref={inputRef}
        type="text"
        value={symbol}
        autoComplete="off"    
        spellCheck={false}  
        onChange={(e) => {
          console.log("💡 Triggering onSymbolChange with:", e.target.value);
          if (typeof onSymbolChange === "function") {
            onSymbolChange(e.target.value);
          } else {
            console.error("❌ onSymbolChange is NOT a function:", onSymbolChange);
          }
        }}
        onKeyDown={(e) => {
          
          if (e.key === "Enter") {
            e.preventDefault();
            if (typeof onAnalyze === "function" && !loading) {
              onAnalyze();
            }
          }
          
        }}
        placeholder="Enter company name or ticker (e.g., General Motors, GM, Apple, AAPL)"
        className="sm:w-96"
        disabled={loading}   
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
