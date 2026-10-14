# CryptoApp

Projektarbeit **Web Services** (CAMPUS 02, WS 2026/27): eine Microservice-Architektur rund um Krypto-Trading, entwickelt mit ASP.NET Core.

## Services

| Service | Verantwortung | Status |
|---|---|---|
| **AccountService** | Accounts, Guthaben, Portfolio-Wert | implementiert |
| **MarketService** | Coin-Kurse (lesend) | beschrieben |
| **TradingService** | Kauf/Verkauf von Coins, Bestände | beschrieben |

Bounded Contexts, Context Map und Datenmodelle aller Services stehen in [`docs/`](docs/).

## Projektstruktur

```
CryptoProjekt/
├── CryptoApp.slnx      Solution
├── AccountService/     ASP.NET Core Web API
└── docs/               Beschreibungen & Ausarbeitungen
```

## Voraussetzungen

- [.NET SDK 10](https://dotnet.microsoft.com/download)

## Starten

```bash
cd AccountService
dotnet run --launch-profile http
```

Swagger UI: <http://localhost:5219/swagger>

## Team

| Name | Aufgabenbereich |
|---|---|
| | |
| | |
| | |
