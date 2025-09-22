# 📁 Firestore Architecture – Client Confirmation Manager

This document summarizes the Firestore data structure for the **Client Confirmation Manager** tool, incorporating `Trades`, `Matches`, and `Emails`. It also includes a proposed structure for daily `Reports` that aggregates status and confirmation activity for client-facing reporting and dashboards.

---

## 🔄 Core Collections Overview

### 1. 🧾 `trades` (Base Layer)
These represent the trades uploaded by the client and serve as the foundation of the system.

**Key Fields:**
```json
{
  "tradeId": "auto-generated",
  "counterpartyName": "Itaú",
  "productType": "Spot",
  "direction": "Sell",
  "currency1": "USD",
  "currency2": "CLP",
  "amount": 100000,
  "price": 998,
  "tradeDate": "2025-10-01",
  "paymentDate": "2025-10-01",
  "settlementType": "Entrega Física",
  "matchId": null,  // updated upon confirmation
  "uploadSessionId": "abc123",
  "organizationId": "xyz-corp",
  "status": "unmatched"  // or matched/confirmed
}
```

---

### 2. 🔗 `matches` (Matching Engine Output)
System-generated confirmations that link `trades` and `emails`.

**Key Fields:**
```json
{
  "matchId": "match456",
  "tradeId": "trade123",
  "emailId": "email789",
  "confidenceScore": 100,
  "matchReasons": [
    "Counterparty exact",
    "Trade date exact",
    "Amount exact",
    "Product type exact"
  ],
  "status": "confirmed",
  "organizationId": "xyz-corp"
}
```

---

### 3. 📧 `emails` (Parsed Email Confirmations)
Parsed and processed email confirmations from banks or counterparties.

**Key Fields:**
```json
{
  "emailId": "email789",
  "sender": "ben.clark@palace.cl",
  "subject": "FW: Itau Confirmation Trade T0001",
  "confirmationDetected": true,
  "processedAt": "2025-10-01T12:19:08Z",
  "numTradesConfirmed": 1,
  "organizationId": "xyz-corp",
  "uploadSessionId": "abc123",
  "trades": [  // mirrored or parsed trade(s)
    {
      "amount": 100000,
      "direction": "Sell",
      "price": 998,
      "currencyPair": "USD/CLP",
      "tradeDate": "2025-10-01",
      "matchId": "match456"
    }
  ]
}
```

---

## 📅 `clients/{clientId}/reports/{reportId}` – Daily Summary Report
Each client will have their own set of daily reports stored in a subcollection. These are generated at end-of-day.

### Report Document Structure:
```json
{
  "reportDate": "2025-10-01",
  "clientId": "xyz-corp",
  "trades": [
    {
      "tradeId": "trade123",
      "counterpartyName": "Itaú",
      "productType": "Spot",
      "direction": "Sell",
      "amount": 100000,
      "currencyPair": "USD/CLP",
      "tradeDate": "2025-10-01",
      "matchStatus": "fully matched", // unmatched / partial / fuzzy
      "fieldsMatch": true,  // all fields align
      "emailSent": true,
      "settlementInstructionSent": false
    }
  ],
  "matches": [
    {
      "matchId": "match456",
      "tradeId": "trade123",
      "emailId": "email789",
      "matchReasons": ["Counterparty exact", "Amount exact"],
      "status": "confirmed"
    }
  ],
  "emails": [
    {
      "emailId": "email789",
      "sender": "ben.clark@palace.cl",
      "subject": "FW: Itau Confirmation Trade T0001",
      "numTradesConfirmed": 1,
      "processedAt": "2025-10-01T12:19:08Z"
    }
  ],
  "logs": [
    {
      "timestamp": "2025-10-01T23:59:59Z",
      "action": "End-of-day report generated",
      "performedBy": "system"
    }
  ]
}
```

---

## 📊 Reporting UI (React + Apache ECharts)

You can build an interactive front end using:
- **Client dropdown + Date Range Picker**
- **Dynamic summary charts** (matched vs unmatched, email status)
- **Tabular report with expandable trade rows**
- **Downloadable reports** (CSV, PDF)
- **Filters** by status, counterparty, confirmation status, etc.

---

## ✅ Next Steps
1. Ensure `emailSent`, `settlementInstructionSent`, `fieldsMatch`, etc., are logged in real time.
2. Add end-of-day Cloud Function to generate `reports/{reportId}` from current day’s data.
3. Build report viewer for clients and internal audit users.

---

Let me know if you want TypeScript interfaces or a Notion-ready version next.

