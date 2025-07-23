import React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

const Header = () => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header className="w-full py-6 px-4 bg-gradient-to-r from-indigo-600 to-purple-700 text-white shadow">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">
          Echo<span className="text-yellow-300">Market</span>
        </h1>
        <div className="flex items-center gap-4">
          <p className="text-sm opacity-80 hidden sm:block">
            Powered by <a href="https://www.tavily.com" target="_blank" className="underline hover:text-white">Tavily</a>
          </p>
          {mounted && (
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md bg-white/10 hover:bg-white/20 transition"
              aria-label="Toggle Theme"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
