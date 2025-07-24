// Import React, ReactDOM, main App, global styles, and theme provider
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { ThemeProvider } from "@/components/ui/theme-provider";

// Render the app inside the root element
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/* Wrap the app in ThemeProvider for light/dark mode support */}
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
