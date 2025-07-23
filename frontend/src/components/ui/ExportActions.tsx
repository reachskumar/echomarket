import React from "react";

interface Props {
  resultData: Record<string, any>;
}

const ExportActions = ({ resultData }: Props) => {
  const exportCSV = () => {
    const csv = Object.entries(resultData)
      .map(([key, value]) => `"${key}","${String(value).replace(/"/g, '""')}"`)
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "echomarket_analysis.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportPDF = () => {
    alert("PDF export coming soon.");
  };

  return (
    <div className="flex justify-center gap-4 mt-6">
      <button
        onClick={exportCSV}
        className="bg-primary text-white px-4 py-2 rounded-xl shadow hover:bg-primary/90"
      >
        ⬇️ Export CSV
      </button>
      <button
        onClick={exportPDF}
        className="bg-secondary text-white px-4 py-2 rounded-xl shadow hover:bg-secondary/90"
      >
        🧾 Export PDF
      </button>
    </div>
  );
};

export default ExportActions;
