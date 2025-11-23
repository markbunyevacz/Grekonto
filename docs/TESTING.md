# Tesztelési Útmutató

**Projekt**: Grekonto AI Automatizáció
**Dátum**: 2025-11-22
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-22
**Commit**: TBD (frissítés után)

---

## 🧪 Tesztelési Stratégia

### Unit Tesztek
- Minden függvény tesztelve
- Mock adatok
- Hibakezelés

### Integration Tesztek
- API végpontok
- Table Storage
- Audit log

### End-to-End Tesztek
- Teljes workflow
- DLQ trigger
- Orchestration

---

## 🔴 DLQ Tesztelés

### Teszt 1: Hibás Dokumentum
```bash
# Trigger hibás dokumentumot
curl -X POST http://localhost:7071/api/upload \
  -F "file=@invalid.txt"

# Várj 30 másodpercet (3 retry)

# Ellenőrizd a DLQ-t
curl http://localhost:7071/api/dlq
```

**Várható**: DLQ elem `PENDING_REVIEW` státusszal

### Teszt 2: DLQ Feloldása
```bash
curl -X POST http://localhost:7071/api/dlq/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "dlq_id": "<id>",
    "resolution_status": "RESOLVED",
    "resolution_notes": "Manuálisan feldolgozva"
  }'
```

**Várható**: `{"success": true}`

---

## 🟡 Secret Rotation Tesztelés

### Teszt 1: Secret Status
```bash
curl http://localhost:7071/api/secret-status
```

**Várható**:
```json
{
  "success": true,
  "secrets_checked": 4,
  "needs_rotation": 0,
  "secrets": {
    "email-password": {
      "age_days": 15,
      "should_rotate": false
    }
  }
}
```

### Teszt 2: Timer Trigger
- Automatikus futás: 1. nap 00:00
- Audit log: `SECRET_ROTATION_CHECK`

---

## 🟢 Orchestration Tesztelés

### Teszt 1: Orchestration Indítása
```bash
# Upload dokumentum
curl -X POST http://localhost:7071/api/upload \
  -F "file=@invoice.pdf"

# Jegyezd fel az instance ID-t az audit logból
```

### Teszt 2: Status Lekérése
```bash
curl "http://localhost:7071/api/orchestration-status?instance_id=<id>"
```

**Várható**:
```json
{
  "success": true,
  "runtime_status": "Completed",
  "output": {...}
}
```

---

## 📊 Audit Log Ellenőrzés

```bash
curl http://localhost:7071/api/audit-logs
```

**Várható események**:
- `PROCESSING_STARTED`
- `PROCESSING_FAILED_DLQ`
- `DLQ_ITEM_RESOLVED`
- `SECRET_ROTATED`
- `ORCHESTRATION_STARTED`

---

## ✅ Tesztelési Checklist

- [ ] DLQ: Hibás dokumentum DLQ-ba kerül
- [ ] DLQ: API működik
- [ ] DLQ: Elem feloldható
- [ ] Secret: Status API működik
- [ ] Secret: Timer trigger működik
- [ ] Orchestration: Indul
- [ ] Orchestration: Status API működik
- [ ] Audit: Összes esemény naplózva

---

## 🐛 Hibaelhárítás

| Probléma | Megoldás |
|----------|----------|
| DLQ nem működik | Ellenőrizd: Table Storage, Exception handler |
| Secret Rotation nem működik | Ellenőrizd: Key Vault, KEY_VAULT_NAME env var |
| Orchestration nem működik | Ellenőrizd: Durable Functions SDK, Activity functions |

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v1.0** (2025-11-22): Eredeti verzió - Teljes tesztelési útmutató dokumentálva

