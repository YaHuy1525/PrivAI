"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [ast, setAst] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [selectedFunction, setSelectedFunction] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/parse", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to parse the file.");
      }

      const data = await response.json();
      setAst(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setAst(null);
    }
  };

  const handleSummarize = async (func: any) => {
    const code = func.type === 'FunctionDefinition' ? func.name : null;
    if (!code) {
      setError("Could not find function to summarize.");
      return;
    }

    setSelectedFunction(code);

    const formData = new FormData();
    formData.append("code", JSON.stringify(func));


    try {
      const response = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to summarize the function.");
      }

      const data = await response.json();
      setSummary(data.summary);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setSummary(null);
    }
  };

  const renderAst = (node: any) => {
    if (!node) {
      return null;
    }

    if (Array.isArray(node)) {
      return node.map((item, index) => <div key={index}>{renderAst(item)}</div>);
    }

    if (typeof node === "object" && node !== null) {
      if (node.type === "FunctionDefinition") {
        return (
          <div className="bg-gray-700 p-4 rounded-lg mb-4">
            <h3 className="text-xl font-bold mb-2">{node.name}</h3>
            <button
              onClick={() => handleSummarize(node)}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Summarize
            </button>
            {selectedFunction === node.name && summary && (
              <div className="bg-gray-600 p-4 rounded-lg mt-4">
                <h4 className="text-lg font-bold mb-2">Summary</h4>
                <p>{summary}</p>
              </div>
            )}
          </div>
        );
      }
      return Object.keys(node).map((key) => (
        <div key={key} className="ml-4">
          {renderAst(node[key])}
        </div>
      ));
    }
    return null;
  };


  return (
    <main className="flex min-h-screen flex-col items-center p-24 bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-8">ChainSight</h1>
      <p className="text-lg mb-8">
        AI-Powered Smart Contract Risk Analyzer
      </p>

      <div className="w-full max-w-2xl">
        <div className="bg-gray-800 p-6 rounded-lg mb-8">
          <h2 className="text-2xl font-bold mb-4">Upload a Solidity File</h2>
          <input
            type="file"
            onChange={handleFileChange}
            className="mb-4 p-2 rounded bg-gray-700"
            accept=".sol"
          />
          <button
            onClick={handleUpload}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Analyze
          </button>
        </div>

        {error && <div className="bg-red-500 text-white p-4 rounded-lg mb-8">{error}</div>}

        {ast && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
            {renderAst(ast)}
          </div>
        )}
      </div>
    </main>
  );
}
