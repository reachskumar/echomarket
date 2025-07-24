// Main Home Page Component
// 
// This is the heart of the app - handles user input, calls the backend API,
// and displays all the analysis results. The flow is pretty simple:
// 1. User types in a company name or ticker
// 2. We try to detect the ticker if they entered a company name
// 3. We call our backend API to get the analysis
// 4. We display all the results in different components

import React, { useState } from "react";
import Header from "@/components/ui/Header";
import SearchBar from "@/components/ui/SearchBar";
import InsightSummary from "@/components/ui/InsightSummary";
import { ExecutiveSummaryRow } from "@/components/ui/ExecutiveSummaryRow";
import AIRecommendationCard from "@/components/ui/AIRecommendationCard";
import { MarketNews } from "@/components/ui/MarketNews";
import { PriceTrendChart } from "@/components/ui/PriceTrendChart";
import ExportActions from "@/components/ui/ExportActions";
import { TrendAnalysisSection } from "@/components/ui/TrendAnalysisSection";
import Loader from "@/components/ui/Loader";
import { PriceStats } from "@/components/ui/PriceStats";

// Quick lookup for common company names - saves API calls for popular stocks
const tickerMap: Record<string, string> = {
  "general motors": "GM",
  "apple": "AAPL",
  "microsoft": "MSFT", 
  "google": "GOOGL",
  "alphabet": "GOOGL",
  "tesla": "TSLA",
  "nvidia": "NVDA",
  "amazon": "AMZN",
  "meta": "META",
  "facebook": "META"
};

// Structure of data we get back from the backend
interface AnalysisResult {
  symbol: string;
  price: number | string;
  prices: Record<string, number>;
  sentiment: string;
  confidence: number;
  summary: string;
  trend: {
    direction: string;
    strength: string;
    confidence: number;
    risk: string;
    timeframe: string;
    keyFactors: string[];
    summary?: string;
  };
  recommendation: string;
  insight: string;
  news: { title: string; url: string; snippet: string }[];
  chart_url: string;
}

const Home: React.FC = () => {
  // State for symbol, loading, data, and error
  const [symbol, setSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");

  // Try to figure out the ticker symbol from a company name using backend API
  const detectTicker = async (companyName: string): Promise<string | null> => {
    try {
      const response = await fetch(`http://localhost:8000/detect-ticker?company=${encodeURIComponent(companyName)}`);
      if (!response.ok) return null;
      const result = await response.json();
      return result.ticker || null;
    } catch (error) {
      console.error("Ticker detection failed:", error);
      return null;
    }
  };

  // Call backend API to run the full analysis pipeline
  const fetchAnalysis = async (ticker: string) => {
    try {
      setLoading(true);
      setError("");
      const res = await fetch(`http://localhost:8000/ui/analyze/${ticker}`, {
        method: "GET",
      });
      if (!res.ok) throw new Error("Failed to fetch analysis");
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error(err);
      setError("Unable to fetch data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Update symbol state when user types
  const handleSymbolChange = (value: string) => {
    setSymbol(value);
  };

  // Start the analysis process
  const handleAnalyzeClick = () => {
    handleAnalyzeClickAsync();
  };

  // Handles analyze button click: resolves ticker, validates, and fetches analysis
  const handleAnalyzeClickAsync = async () => {
    if (!symbol) {
      setError("Please enter a valid company name or ticker symbol");
      return;
    }
    setLoading(true);
    setError("");

    let input = symbol.trim();
    let resolvedTicker = input.toUpperCase();
    // Robust ticker resolution: always use quick lookup if available
    const quickLookup = tickerMap[input.toLowerCase()];
    if (quickLookup) {
      resolvedTicker = quickLookup.toUpperCase();
      if (symbol !== resolvedTicker) setSymbol(resolvedTicker);
    } else if (/^[A-Z]{1,5}$/.test(resolvedTicker)) {
      // If it looks like a ticker, use as is
      // Optionally, validate against a list of real tickers
    } else {
      // Use backend API to detect ticker from company name
      try {
        const detected = await detectTicker(input);
        if (detected) {
          resolvedTicker = detected.toUpperCase();
          if (symbol !== resolvedTicker) setSymbol(resolvedTicker);
        } else {
          setError(`Could not find ticker for "${input}". Please try using the ticker symbol directly (e.g., GM for General Motors).`);
          setLoading(false);
          return;
        }
      } catch (error) {
        setError("Failed to detect ticker. Please try using the ticker symbol directly.");
        setLoading(false);
        return;
      }
    }
    // Final validation: resolvedTicker must be a valid ticker format
    if (!/^[A-Z]{1,5}$/.test(resolvedTicker)) {
      setError(`"${resolvedTicker}" is not a valid ticker symbol. Please enter a valid ticker (e.g., AAPL, TSLA).`);
      setLoading(false);
      return;
    }
    // Now run the actual analysis with the resolved ticker
    console.log("Final resolved ticker to analyze:", resolvedTicker);
    fetchAnalysis(resolvedTicker);
  };

  // Figure out price changes for display
  console.log("Fetched analysis data:", data);
  console.log("Price in UI:", data?.price, typeof data?.price);

  const lastPrice = (typeof data?.price === 'number' && isFinite(data.price) && data.price > 0)
    ? data.price
    : undefined;
  // let lastPriceRaw = (typeof data?.price === 'number' && data.price > 0) ? data.price : undefined;
  // lastPriceRaw is commented out for now, uncomment if needed for future use
  
  // Calculate price change using historical data
  let priceChange = 0;
  let priceChangePercent = 0;
  if (lastPrice && data?.prices) {
    const priceEntries = Object.entries(data.prices).sort(([a], [b]) => a.localeCompare(b));
    if (priceEntries.length >= 2) {
      // Compare current price to previous day's price
      const prevPrice = priceEntries[priceEntries.length - 2][1];
      priceChange = lastPrice - prevPrice;
      priceChangePercent = prevPrice ? (priceChange / prevPrice) * 100 : 0;
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground relative">
      {loading && <Loader />}
      <Header />

      
      <SearchBar
        symbol={symbol}
        onSymbolChange={handleSymbolChange}
        onAnalyze={handleAnalyzeClick}
        loading={loading}
      />

      <main className="max-w-6xl mx-auto px-4 py-12 space-y-10">
        {error && <p className="text-red-500 text-center text-lg font-medium mb-4">{error}</p>}

        {/* Show all analysis results when not loading and data is available */}
        {!loading && data && (
          <div className="space-y-8">
            <ExecutiveSummaryRow
              price={typeof data.price === 'number' ? data.price : undefined}
              sentiment={data.sentiment}
              recommendation={data.recommendation}
              confidence={data.confidence}
              riskLevel={data.trend?.risk}
            />

            <InsightSummary summary={data.summary || "No summary available."} ticker={symbol} />

            
            <AIRecommendationCard
              recommendation={data.recommendation}
              insight={data.insight}
            />

            
            <TrendAnalysisSection
              trend={data.trend}
            />

            
            <PriceTrendChart
              symbol={symbol}
              prices={data.prices || {}}
              currentPrice={lastPrice || 0}
            />

            
            <MarketNews
              news={
                (data.news || []).map((n) => ({
                  title: n.title,
                  snippet: n.snippet,
                  url: n.url,
                }))
              }
              ticker={symbol}
            />

            
            <ExportActions
              ticker={symbol}
              onExportPDF={() => {
                const url = `http://localhost:8000/analyze/${symbol}/export/pdf`;
                window.open(url, '_blank');
              }}
              onExportCSV={() => {
                const url = `http://localhost:8000/analyze/${symbol}/export/csv`;
                window.open(url, '_blank');
              }}
            />

            
            <PriceStats
              symbol={symbol}
              price={lastPrice || 0}
              priceChange={priceChange}
              priceChangePercent={priceChangePercent}
            />
          </div>
        )}
      </main>
      
      <div className="w-full border-t border-border mt-10 pt-6 pb-4 bg-background dark:bg-background flex flex-col items-center">
        <span className="text-base text-muted text-center">
          <span className="font-semibold text-blue-700 dark:text-blue-400">EchoMarket</span> &ndash; Your Intelligent Market Assistant
        </span>
      </div>
    </div>
  );
};

export default Home; 