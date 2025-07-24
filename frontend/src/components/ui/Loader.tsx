// Loading Spinner Component
// Shows a spinning animation when the app is processing something.


import React from "react";

const Loader: React.FC = () => {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex flex-col items-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        
        <p className="text-gray-600 text-sm">
          Analyzing stock data...
        </p>
        
        <p className="text-gray-400 text-xs max-w-xs text-center">
          This usually takes 10-30 seconds while we gather price data, 
          news articles, and run AI analysis.
        </p>
      </div>
    </div>
  );
};

export default Loader;
  
