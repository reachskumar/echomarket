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

const tickerMap: Record<string, string> = {
  google: "GOOGL",
  alphabet: "GOOGL",
  nvidia: "NVDA",
  apple: "AAPL",
  microsoft: "MSFT",
  wipro: "WIPRO",
  tesla: "TSLA",
};

const Home: React.FC = () => {
  const [symbol, setSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  const fetchAnalysis = async (ticker: string) => {
    try {
      setLoading(true);
      setError("");
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ticker }),
      });
      if (!res.ok) throw new Error("Failed to fetch analysis");
      const result = await res.json();
      console.log("📊 Analysis result:", result);
      setData(result);
      console.log("FULL AGENT RESPONSE:", result);
    } catch (err) {
      console.error(err);
      setError("Unable to fetch data. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  

  const handleSymbolChange = (newSymbol: string) => {
    setSymbol(newSymbol.toUpperCase());
    setError("");
  };

  const handleAnalyzeClick = () => {
    if (!symbol) {
      setError("Please enter a valid company or ticker");
      return;
    }

    const resolved = tickerMap[symbol.toLowerCase()] || symbol;
    fetchAnalysis(resolved.toUpperCase());
  };

  let lastPrice = 0;
  let prevPrice = 0;
  let priceChange = 0;
  let priceChangePercent = 0;

  if (data?.prices) {
    const priceEntries = Object.entries(data.prices).sort(
      ([dateA], [dateB]) => new Date(dateA).getTime() - new Date(dateB).getTime()
    );
    lastPrice = priceEntries.at(-1)?.[1] || 0;
    prevPrice = priceEntries.at(-2)?.[1] || 0;
    priceChange = lastPrice - prevPrice;
    priceChangePercent = (priceChange / (prevPrice || 1)) * 100;
  }

  return (
    <div className="min-h-screen bg-background text-foreground relative">
      {loading && <Loader />}
      <Header />

      <SearchBar
        key={`searchbar-${symbol}`}
        symbol={symbol}
        onSymbolChange={handleSymbolChange}
        onAnalyze={handleAnalyzeClick}
        loading={loading}
      />

      <main className="max-w-6xl mx-auto px-4 py-10 space-y-8">
        {error && <p className="text-red-500 text-center">{error}</p>}

        {!loading && data && (
          <>
            <ExecutiveSummaryRow
              sentimentScore={Math.round((data.confidence || 0) * 100)}
              sentimentLabel={data.sentiment || "Neutral"}
              currentPrice={lastPrice}
              priceChange={priceChange}
              priceChangePercent={priceChangePercent}
              analysisScore={Math.round((data.confidence || 0) * 100)}
            />

            <InsightSummary summary={data.summary || "No summary available."} />

            <AIRecommendationCard
              insight={data.insight}
              action={data.recommendation}
              confidence={Math.round((data.confidence || 0) * 100)}
              risk="Medium"
              timeHorizon="2–4 weeks"
              recommendationExplanation={data.insight}
            />

            <TrendAnalysisSection
              summary={data.trend?.summary || "N/A"}
              direction={data.trend?.direction || "neutral"}
              strength={data.trend?.strength || "weak"}
              confidence={data.trend?.confidence || 0}
              keyFactors={data.trend?.keyFactors || []}
              timeframe={data.trend?.timeframe || "unknown"}
              riskLevel={data.trend?.riskLevel || "unknown"}
            />

            <PriceTrendChart
              data={Object.entries(data.prices || {}).map(([date, price]) => ({
                date,
                price,
              }))}
              symbol={symbol}
            />

            <MarketNews
              news={
                data.news?.map((n: any) => ({
                  title: n.title,
                  snippet: n.snippet,
                  link: n.url,
                  source: "AI",
                  publishedAt: "N/A",
                  sentiment: "neutral",
                })) || []
              }
            />

            <ExportActions
              symbol={symbol}
              summary={data.summary}
              onExportCSV={() =>
                window.open(`http://localhost:8000/analyze/${symbol}/export/csv`)
              }
              onExportPDF={() =>
                window.open(`http://localhost:8000/analyze/${symbol}/export/pdf`)
              }
            />
          </>
        )}
      </main>
    </div>
  );
};

export default Home;
