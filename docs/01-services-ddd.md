# Phase 1: Domain Driven Design – Crypto Brokerage Plattform

> **Hinweis zur Umsetzung:** Alle drei Services sind in diesem Dokument beschrieben (Aufgabe 1). Implementiert ist nur der **AccountService**, da laut Angabe ein Controller mit CRUD-Funktionalität genügt.

## Überblick

Die Plattform ermöglicht es Nutzern, ein Konto zu eröffnen, aktuelle Kryptokurse abzurufen und Kryptowährungen zu kaufen bzw. zu verkaufen. Nach den Prinzipien von **Domain Driven Design** wird die Domäne in drei **Bounded Contexts** aufgeteilt. Jeder davon wird als eigenständiger Microservice mit **eigener Datenbank** umgesetzt (*Decentralized Data Management* nach Fowler). Die Services kommunizieren ausschließlich über REST-Schnittstellen und referenzieren fremde Entitäten nur über IDs, nie über gemeinsame Tabellen.

---

## Service 1: Account Service

**Aufgabe:** Kundenverwaltung und Fiat-Guthaben (EUR).

**Funktionen:** Konto eröffnen, Kundendaten abfragen/ändern, Konto stilllegen (sperren), Konto löschen, Guthaben einzahlen/abbuchen.

> **Umsetzung:** In der Implementierung werden `User` und `CashBalance` zu einer Entität `Account` mit dem Feld `Balance` vereinfacht (siehe API-Vertrag).

### Bounded Context: Kundenidentität & Geldkonto

Hier geht es nur um die Fragen: *Wer ist der Kunde, ist er verifiziert und wie viel Geld hat er?* Kurse und Trades kennt dieser Service nicht. Der Begriff „Konto“ bedeutet hier immer das Kundenkonto mit Fiat-Guthaben.

### Datenmodell

| Entität | Attribut | Typ |
|---|---|---|
| **User** | UserId | Guid (PK) |
| | Vorname, Nachname | string |
| | Email | string (unique) |
| | Telefonnummer | string |
| | Geburtsdatum | DateOnly |
| | Steuernummer | string |
| | Staatsbürgerschaft | string (ISO-3166 Ländercode) |
| | KycStatus | Enum: `Pending`, `Verified`, `Rejected` |
| | BiometrieReferenzId | string (Referenz auf externen Ident-Anbieter) |
| | AccountStatus | Enum: `Active`, `Suspended`, `Closed` |
| | CreatedAt | DateTime |
| **CashBalance** | UserId | Guid (FK) |
| | Currency | string (z. B. `EUR`) |
| | Available | decimal |
| | Reserved | decimal (für offene Orders blockiert) |

> **Hinweis:** Biometrische Daten sind nach DSGVO Art. 9 besonders schutzwürdig. Deshalb speichert der Service keine Rohdaten (Fingerabdruck, Gesichtsbild), sondern nur das Ergebnis der Identitätsprüfung (`KycStatus`) und eine Referenz-ID.

### Datenvalidierung

- Email: Pflichtfeld, gültiges Format, im System eindeutig
- Alter ≥ 18 Jahre (aus dem Geburtsdatum berechnet)
- Steuernummer: Pflichtfeld, gültiges Format (AT: 9-stellig)
- Staatsbürgerschaft: gültiger ISO-Ländercode, Nachweis Pflicht für `KycStatus = Verified`
- Telefonnummer im E.164-Format (z. B. `+43…`)
- `Available` ≥ 0 und `Reserved` ≥ 0, das Guthaben darf nie negativ werden
- Eine Einzahlung bzw. Abbuchung muss > 0 sein
- Ein Konto mit Status `Suspended` oder `Closed` kann nicht handeln; löschen geht nur bei Guthaben = 0 und ohne offene Positionen

---

## Service 2: Market Data Service

**Aufgabe:** Aktuelle Kryptokurse bereitstellen (nur lesend für andere Services).

**Funktionen:** Liste handelbarer Assets, aktueller Kurs pro Asset, einfache Kurshistorie.

### Bounded Context: Marktinformationen

Der Service kümmert sich nur um Assets und Preise. Er weiß nichts über Nutzer oder Orders. Die Kurse holt er von einem externen Anbieter (im Projekt simuliert, die URL liegt in der `appsettings.json`).

### Datenmodell

| Entität | Attribut | Typ |
|---|---|---|
| **CryptoAsset** | Symbol | string (PK, z. B. `BTC`) |
| | Name | string (z. B. `Bitcoin`) |
| | IsTradable | bool |
| | MinOrderQuantity | decimal |
| **PriceTicker** | Symbol | string (FK) |
| | PriceEur | decimal |
| | Timestamp | DateTime |
| | Source | string |

### Datenvalidierung

- Symbol: Pflichtfeld, 2–10 Großbuchstaben, muss als `CryptoAsset` existieren
- `PriceEur` > 0
- Timestamp darf nicht in der Zukunft liegen
- Kurse älter als 30 Sekunden gelten als veraltet und werden nicht für Trades verwendet
- Ein unbekanntes Symbol liefert `404 Not Found`

---

## Service 3: Trading Service

**Aufgabe:** Orders ausführen und Krypto-Bestände verwalten.

**Funktionen:** Kaufen, Verkaufen, Orderhistorie, Portfolioübersicht.

### Bounded Context: Handel & Depotführung

Hier liegt die eigentliche Geschäftslogik des Brokers. Der Service besitzt die Orders und die Krypto-Bestände (Depot). Kundendaten und Kurse speichert er nicht selbst, die fragt er beim jeweils zuständigen Service ab.

### Datenmodell

| Entität | Attribut | Typ |
|---|---|---|
| **TradeOrder** | OrderId | Guid (PK) |
| | UserId | Guid (Referenz auf Account Service) |
| | Symbol | string (Referenz auf Market Data Service) |
| | Side | Enum: `Buy`, `Sell` |
| | Quantity | decimal |
| | ExecutedPrice | decimal |
| | Fee | decimal |
| | TotalAmount | decimal |
| | Status | Enum: `Pending`, `Executed`, `Rejected` |
| | CreatedAt | DateTime |
| **PortfolioPosition** | UserId | Guid |
| | Symbol | string |
| | Quantity | decimal |
| | AverageBuyPrice | decimal |

### Datenvalidierung

- Quantity > 0 und ≥ `MinOrderQuantity` des Assets
- Side muss `Buy` oder `Sell` sein
- Kauf: verfügbares Guthaben ≥ Menge × Kurs + Gebühr
- Verkauf: Bestand im Depot ≥ Verkaufsmenge (keine Leerverkäufe)
- Nur Nutzer mit `AccountStatus = Active` und `KycStatus = Verified` dürfen handeln
- Das Asset muss `IsTradable = true` sein und einen aktuellen Kurs haben

---

## Context Map

```
                ┌────────────────────────┐
                │ Externer Kursanbieter  │
                └───────────┬────────────┘
                            │ ACL (Anti-Corruption Layer)
                            ▼
┌──────────────────┐   ┌──────────────────────┐
│ Account Service  │   │ Market Data Service  │
│   (Upstream)     │   │ (Upstream, OHS / PL) │
└────────┬─────────┘   └──────────┬───────────┘
         │ Customer/Supplier      │ Open Host Service
         ▼                        ▼
       ┌────────────────────────────┐
       │      Trading Service       │
       │       (Downstream)         │
       └────────────────────────────┘
```

| Beziehung | Muster | Bedeutung |
|---|---|---|
| Account → Trading | **Customer/Supplier** | Trading ist der „Kunde“ und braucht Kundenstatus und Guthaben. Account stellt dafür eine stabile API bereit und reserviert bzw. bucht Beträge auf Anfrage. |
| Market Data → Trading | **Open Host Service + Published Language** | Market Data bietet eine öffentliche, standardisierte REST-API (JSON) an, die jeder Service nutzen kann, nicht nur Trading. |
| Externer Anbieter → Market Data | **Anti-Corruption Layer** | Das Datenformat des externen Anbieters wird in unser eigenes `PriceTicker`-Modell übersetzt. Wechselt der Anbieter, betrifft das nur diese Übersetzungsschicht. |

Account und Market Data kennen sich gegenseitig nicht – es gibt keine direkte Abhängigkeit zwischen den beiden.

---

## Ablauf eines Trades (Kauf)

1. Der Client schickt `POST /api/v1/brokerage/execute-trade` an den **Trading Service** (abgesichert über einen API-Key).
2. Trading fragt beim **Account Service** nach, ob der User existiert, aktiv und KYC-verifiziert ist.
3. Trading holt den aktuellen Kurs beim **Market Data Service**. Ist der Kurs älter als 30 Sekunden, wird die Order abgelehnt.
4. Trading berechnet den Gesamtbetrag (Menge × Kurs + Gebühr) und lässt den Account Service diesen Betrag **reservieren**. Bei zu wenig Guthaben gibt es eine Ablehnung mit `422 Unprocessable Entity`.
5. Trading führt die Order aus, speichert die `TradeOrder` und aktualisiert die `PortfolioPosition`.
6. Trading bestätigt die Buchung beim Account Service, das reservierte Geld wird endgültig abgebucht.
7. Schlägt Schritt 5 fehl, wird die Reservierung wieder freigegeben (**Kompensation**). So bleiben die Daten konsistent, obwohl jeder Service seine eigene Datenbank hat.

Beim **Verkauf** läuft es umgekehrt: Zuerst wird der Depotbestand geprüft, dann der Kurs geholt, die Position reduziert und das Guthaben gutgeschrieben.
