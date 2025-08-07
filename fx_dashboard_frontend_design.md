
# FX Trade Ranking Dashboard — Frontend Mock Design

## Overview

This project aims to create a visually compelling, front-end-only prototype of an FX trade ranking dashboard using mock data in CSV format. The core idea is to provide banks with access to client activity insights they don’t currently have — showing where they stand relative to competitors in terms of winning trades, volumes, and trends.

Banks often have visibility only into the trades they win or quote on, but not into what they’ve lost — or who the client ultimately traded with. This dashboard bridges that gap. It allows banks to:

- Benchmark their share of wallet with each client in FX products.
- Understand whether they are improving or declining in rank over time.
- Identify missed opportunities: cases where they quoted but didn’t win, and whether the client traded that product with someone else.

This tool is designed to be informative, visually attractive, and privacy-conscious, revealing actionable trends without compromising counterparty confidentiality.

---

## Objectives

- Visualize client trade activity and counterparty bank rankings.
- Allow users to explore historical trends and missed trade opportunities.
- Ensure confidentiality by anonymizing competitor identities.

---

## 1. Data Design

### 1.1 Primary Data File: `sample_trades.csv`

This file contains the core trade data. Each row represents a trade executed by a client with a specific bank.

**Fields:**

- `Trade ID` — unique identifier for each trade  
- `Client Name` — name of the client  
- `Counterparty Name` — bank executing the trade  
- `Trade Date` — when the trade was agreed  
- `Value Date` — settlement date  
- `Product Type` — FX Spot, Forward, or Swap  
- `Currency Pair` — e.g., USD/CLP  
- `Notional Amount` — trade size in base currency  
- `Rate` — agreed exchange rate  
- `Side` — Buy or Sell from client's perspective

---

## 2. Frontend Structure

The application will be built using **React**.

### 2.1 Components

- **Dashboard View**
  - Client selector
  - Aggregated trade metrics
  - Ranking chart of counterparties
  - Historical ranking trend (line chart)

- **Missed Opportunity Tool**
  - Trade search/filter panel
  - Table showing “we quoted but lost” trades
  - Indicator if the trade happened with another party

---

## 3. CSV Integration

### 3.1 Data Loading

Use a CSV parsing library like `papaparse` to load `sample_trades.csv` into the frontend.

```js
import Papa from 'papaparse';

Papa.parse('/path/to/sample_trades.csv', {
  header: true,
  download: true,
  complete: (results) => {
    console.log(results.data);
  }
});
```

---

## 4. Data Visualization

For rendering charts and visualizations, we recommend using **Apache ECharts**.

### Why ECharts?

- **Commercial-friendly**: Open-source under Apache 2.0 license
- **Highly secure**: No external telemetry or data sharing
- **Powerful and flexible**: Supports interactive charts, drilldowns, animations, and real-time updates
- **Cloud-ready**: Fully compatible with static frontends deployed on platforms like **Google Cloud Run**, **Cloud Storage**, or **Firebase Hosting**
- **Self-hostable**: Can be bundled with your app to avoid any reliance on third-party CDNs

### Installation

```bash
npm install echarts
```

### Basic Example (React or Vanilla JS)

```js
import * as echarts from 'echarts';

const chart = echarts.init(document.getElementById('main'));
chart.setOption({
  title: { text: 'Client Trade Rankings' },
  tooltip: {},
  xAxis: { data: ['You', 'Competitor A', 'Competitor B'] },
  yAxis: {},
  series: [{
    name: 'Volume',
    type: 'bar',
    data: [120, 80, 60]
  }]
});
```

Make sure to include a container with `id="main"` and set a fixed height/width so ECharts can render correctly.

---

## 5. Anonymization Logic

Counterparty rankings should be shown in aggregate form:
- Display rank position (e.g., 3rd out of 8) but not names of other banks.
- Use labels like “Competitor A,” “Competitor B,” etc. only if needed for visual distinction.

---

## 6. Future Expansion

- Replace CSV with API endpoints
- Add user authentication and permissions
- Connect to real-time trade data for live updates
- Extend UI to support alerts and benchmarking summaries

---

## Notes

- This prototype is intended to test UI concepts and confidentiality design before backend integration.
- Keep all logic client-side and use static files for the data.
