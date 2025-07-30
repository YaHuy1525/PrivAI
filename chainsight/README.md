# CHAIN·SIGHT — AI-Powered Smart Contract Risk Analyzer

This project is a web application that uses transformer models to analyze Solidity smart contracts, detect common vulnerabilities, generate natural language summaries of code, and anchor the audit results on the blockchain for verifiability.

## Architecture Overview

```
            ┌─────────────┐
            │ Frontend UI │
            └─────┬───────┘
                  │
        ┌─────────▼────────────┐
        │       Backend        │ ← FastAPI/Node.js
        └────┬───────────┬─────┘
             │           │
  ┌──────────▼───┐ ┌─────▼─────────────┐
  │ ML Inference │ │ Vulnerability DB  │
  └────┬─────────┘ └──────────┬────────┘
       │                     │
 ┌─────▼─────┐        ┌──────▼──────────┐
 │ CodeBERT  │        │ OWASP+SWC Rules │
 └───────────┘        └─────────────────┘
       │
┌──────▼────────┐
│ Blockchain Log│ ← (Audit hash on-chain)
└───────────────┘
```

## Tech Stack

- **AI**: Hugging Face Transformers (CodeBERT, T5)
- **Backend**: FastAPI
- **Frontend**: Next.js + Tailwind CSS
- **Parser**: solidity-parser-antlr
- **Blockchain**: Polygon, Solidity, Ethers.js
- **Hosting**: Vercel (Frontend), Render (Backend), Mumbai Testnet (Blockchain)

## Getting Started

### Prerequisites

- Node.js
- Python 3.8+
- Foundry

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/chainsight.git
   cd chainsight
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies:**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Install smart contract dependencies:**
   ```bash
   cd ../smart_contracts
   forge install
   ```

### Running the Application

1. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Start the backend:**
   ```bash
   cd ../backend
   uvicorn main:app --reload
   ```

3. **Deploy smart contracts:**
   ```bash
   cd ../smart_contracts
   forge script script/Deploy.s.sol --rpc-url <your_rpc_url> --private-key <your_private_key> --broadcast --verify -vvvv
   ```

## License

This project is licensed under the MIT License.
