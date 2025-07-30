"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [ast, setAst] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

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
            <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto">
              {JSON.stringify(ast, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </main>
  );
}
