# Factory Inventory Management System

A full-stack demo application for a Claude Code workshop — inventory management, order tracking, demand forecasting, and analytics for factory operations.

![Dashboard](docs/dashboard-screenshot.png)

## Tech Stack

- **Frontend**: Vue 3 + Vite (port 3000)
- **Backend**: Python FastAPI (port 8001)
- **Data**: In-memory mock data (no database)

## Features

- Dashboard with interactive filtering and key metrics
- Inventory tracking across multiple warehouses
- **Low-Stock Alerts** with urgency-based prioritization and visual indicators
- Order management with status tracking
- Demand forecasting with trend analysis
- Backlog monitoring
- Spending analytics

## Quick Start

**One-command startup:**
```bash
./scripts/start.sh
# Starts both backend and frontend
# Backend: http://localhost:8001
# Frontend: http://localhost:3000
# API Docs: http://localhost:8001/docs
```

**Manual startup:**

Backend:
```bash
cd server
uv venv && uv sync
uv run python main.py
```

Frontend:
```bash
cd client
npm install
npm run dev
```

## API Endpoints

All endpoints support optional filtering via query params: `warehouse`, `category`, `status`, `month`

- `GET /api/inventory` - Inventory items
- `GET /api/inventory/low-stock` - Low-stock items with shortage metrics (sorted by urgency)
- `GET /api/orders` - Orders
- `GET /api/demand` - Demand forecasts
- `GET /api/backlog` - Backlog items
- `GET /api/dashboard/summary` - Summary statistics (includes low_stock_items count)
- `GET /api/spending/*` - Spending data

### Low-Stock Alerts Endpoint

`GET /api/inventory/low-stock?warehouse={warehouse}&category={category}`

Returns inventory items where `quantity_on_hand ≤ reorder_point`, with calculated fields:
- `shortage`: Units below reorder point (reorder_point - quantity_on_hand)
- `shortage_percentage`: Percentage below reorder point ((shortage / reorder_point) × 100)

Items are sorted by urgency (highest shortage percentage first).

**Example response:**
```json
[
  {
    "id": "32",
    "sku": "PSU-508",
    "name": "Battery Backup Power Supply",
    "warehouse": "Tokyo",
    "quantity_on_hand": 75,
    "reorder_point": 100,
    "shortage": 25,
    "shortage_percentage": 25.0
  }
]
```

## Demo Data

Mock data includes:
- Inventory items (Circuit Boards, Sensors, Actuators, Controllers, Power Supplies)
- 32 inventory items across 3 warehouses (San Francisco, London, Tokyo)
- 4 items currently at/below reorder points (low-stock alerts)
- Orders spanning 12 months (Delivered, Shipped, Processing, Backordered)
- Demand forecasts with trends
- Backlog items
- Spending transactions

Data files: `server/data/*.json`

### Low-Stock Alert Thresholds

The system uses a three-tier severity system:
- **Critical** (Red): >30% below reorder point
- **Warning** (Orange): 10-30% below reorder point
- **Low** (Yellow): 0-10% below reorder point (at or just below threshold)

## Production Build

```bash
cd client
npm run build  # Output: client/dist/
```

## Platform Notes

**macOS/Linux:** The one-command startup script (`./scripts/start.sh`) and stop script (`./scripts/stop.sh`) work out of the box.

**Windows:** The shell scripts in `scripts/` are macOS/Linux only. Use the manual startup commands instead — run each in a separate terminal:

Backend:
```bash
cd server
uv venv && uv sync
uv run python main.py
```

Frontend:
```bash
cd client
npm install
npm run dev
```

To stop the servers, press Ctrl+C in each terminal window.

---

**Note:** Demo application with in-memory data. Not production-ready without database, authentication, and security implementation.
