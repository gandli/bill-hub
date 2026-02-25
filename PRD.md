# PRD — BillHub

## 1. Overview

**Product Name:** BillHub
**Tagline:** Snap a bill, track your spending — AI-powered personal finance.
**Target Users:** Individuals who want effortless expense tracking without manual data entry.

## 2. Problem Statement

Most people know they should track spending but find it tedious. Manual entry is a chore, and bank app categorization is too coarse. BillHub automates the process: snap a photo of any receipt/bill, and AI extracts, categorizes, and analyzes the data.

## 3. Core Features

### 3.1 Smart Bill Capture
- Photo OCR: snap receipt → extract merchant, amount, date, items
- PDF import: bank statements, utility bills
- Manual quick-add for cash transactions

### 3.2 Auto-Categorization
- AI categorizes expenses (food, transport, entertainment, utilities, etc.)
- Learn from user corrections over time
- Custom category support

### 3.3 Spending Analytics
- Monthly spending breakdown (pie chart)
- Category trends over time (line chart)
- Budget vs actual comparison
- Unusual spending alerts

### 3.4 Multi-Platform Bill Import
- Alipay/WeChat Pay export CSV
- Bank statement CSV/PDF
- Credit card statement parsing

### 3.5 AI Insights
- "You spent 30% more on dining this month"
- Spending prediction for month-end
- Savings suggestions based on patterns

## 4. Technical Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  React App   │────▶│  Node.js API │────▶│   Firebase   │
│  (Frontend)  │     │  (Backend)   │     │  (Database)  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                  ┌─────────┼─────────┐
                  ▼         ▼         ▼
             ┌────────┐ ┌────────┐ ┌────────┐
             │  OCR   │ │  LLM   │ │ Parser │
             │(Tesseract)│(Categorize)│(CSV/PDF)│
             └────────┘ └────────┘ └────────┘
```

## 5. MVP Scope

| Feature | MVP | V2 |
|---------|-----|----|
| Photo OCR capture | ✅ | |
| Auto-categorization | ✅ | |
| Monthly spending chart | ✅ | |
| CSV import (Alipay/WeChat) | | ✅ |
| AI spending insights | | ✅ |
| Budget tracking | | ✅ |
| PDF bank statement | | ✅ |

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| OCR accuracy on receipts | Use specialized receipt OCR (not general) + user correction |
| Privacy (financial data) | Local-first storage option, encryption at rest |
| Competition (随手记, etc.) | AI-first UX, zero-friction capture |
