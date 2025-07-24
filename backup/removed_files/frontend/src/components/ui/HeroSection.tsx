import React from "react";

const HeroSection: React.FC = () => {
  const scrollToDashboard = () => {
    const section = document.getElementById("dashboard");
    section?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="w-full py-20 bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">
          Echo<span className="text-yellow-400">Market</span>
        </h1>
        <p className="text-lg sm:text-xl text-muted mb-6 max-w-2xl mx-auto">
          Intelligent market research powered by AI. Get insights, sentiment, trends, and predictions — all in one place.
        </p>

        <div className="flex justify-center gap-4">
          <button
            type="button"
            onClick={scrollToDashboard}
            className="px-6 py-3 bg-ring text-background rounded-full text-sm font-medium hover:bg-ring/90 transition duration-200"
            aria-label="Start stock analysis now"
          >
            Start Analysis
          </button>
          <button
            type="button"
            className="px-6 py-3 border border-border rounded-full text-sm font-medium hover:bg-card transition duration-200"
            aria-label="Learn more about EchoMarket"
          >
            Learn More
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
