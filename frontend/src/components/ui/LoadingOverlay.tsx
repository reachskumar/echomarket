import React from "react";
import { Loader2 } from "lucide-react";

const LoadingOverlay: React.FC = () => {
  return (
    <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-40 z-50 flex items-center justify-center">
      <div className="bg-white p-4 rounded-lg shadow-md flex items-center gap-2">
        <Loader2 className="animate-spin h-6 w-6 text-purple-600" />
        <span className="text-sm font-medium text-gray-700">Analyzing data...</span>
      </div>
    </div>
  );
};

export default LoadingOverlay;
