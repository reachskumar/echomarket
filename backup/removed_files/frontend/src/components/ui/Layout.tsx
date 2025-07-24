import React from "react";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="bg-background text-foreground antialiased min-h-screen flex flex-col">
      {/* Optional Header */}
      <header className="w-full border-b border-border py-4 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold tracking-tight">EchoMarket</h1>
          {/* Add dark mode toggle or nav if needed */}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 w-full px-4 py-8 sm:px-6 md:px-10 lg:px-16 max-w-7xl mx-auto">
        {children}
      </main>

      {/* Optional Footer */}
      <footer className="w-full border-t border-border py-4 px-6 text-sm text-muted">
        <div className="max-w-7xl mx-auto text-center">
          &copy; {new Date().getFullYear()} EchoMarket. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Layout;
