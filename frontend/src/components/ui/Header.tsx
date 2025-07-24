// Header Component
// Simple header bar that shows the app name and navigation.

import React from "react";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

const Header: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <header className="bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-500 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 shadow-md px-6 py-6 mb-6">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex flex-col items-center sm:items-start">   
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight drop-shadow-md">
            EchoMarket
          </h1>
          <span className="text-base sm:text-lg text-blue-100 dark:text-gray-300 font-medium mt-1">
            Your Intelligent Market Assistant
          </span>
          <span className="mt-2 text-xs sm:text-sm text-blue-200 dark:text-blue-300 font-semibold bg-blue-100/10 dark:bg-gray-800/40 px-3 py-1 rounded-full shadow-sm">
            Powered by <a href="https://www.tavily.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-300">Tavily</a>
          </span>
        </div>
        <nav className="flex items-center space-x-4 mt-2 sm:mt-0">
          <button
            aria-label="Toggle theme"
            className="rounded-full p-2 hover:bg-blue-200/30 dark:hover:bg-gray-700 transition-colors"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? (
              <Sun size={22} className="text-yellow-300" />
            ) : (
              <Moon size={22} className="text-black" />
            )}
          </button>
        </nav>
      </div>
    </header>
  );
};

// Export the Header component as default
export default Header;
