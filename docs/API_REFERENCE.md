# API Referencia

**Projekt**: Grekonto AI Automatizáció  
**Dátum**: 2025-11-22

---

## 📋 DLQ API-k

### GET /api/dlq
**Leírás**: DLQ elemek lekérése

**Query Parameters**:
- `status` (optional): `PENDING_REVIEW`, `RESOLVED`, `FAILED`

**Válasz**:
```json
{
  "success": true,
  "count": 1,
  "items": [
    {
      "id": "2025-11-22T10:30:45.123456_file_id",
      "file_id": "file_id",
      "blob_name": "20251122/document.pdf",
      "error": "OCR failed",
      "stage": "OCR_STARTED",
      "created_at": "2025-11-22T10:30:45",
      "status": "PENDING_REVIEW"
    }
  ]
}
```

---

### POST /api/dlq/resolve
**Leírás**: DLQ elem feloldása

**Request Body**:
```json
{
  "dlq_id": "2025-11-22T10:30:45.123456_file_id",
  "resolution_status": "RESOLVED",
  "resolution_notes": "Manuálisan feldolgozva"
}
```

**Válasz**:
```json
{
  "success": true,
  "message": "DLQ item resolved"
}
```

---

## 📋 Secret Rotation API-k

### GET /api/secret-status
**Leírás**: Secret rotation status

**Válasz**:
```json
{
  "success": true,
  "secrets_checked": 4,
  "needs_rotation": 0,
  "secrets": {
    "email-password": {
      "age_days": 15,
      "should_rotate": false,
      "max_age_days": 30
    }
  }
}
```

---

## 📋 Orchestration API-k

### GET /api/orchestration-status
**Leírás**: Orchestration status

**Query Parameters**:
- `instance_id` (required): Orchestration instance ID

**Válasz**:
```json
{
  "success": true,
  "instance_id": "abc123",
  "runtime_status": "Completed",
  "input": {...},
  "output": {...},
  "created_time": "2025-11-22T10:30:45",
  "last_updated_time": "2025-11-22T10:31:00"
}
```

**Runtime Status értékek**:
- `Pending` - Várakozás
- `Running` - Futás
- `Completed` - Befejezve
- `Failed` - Sikertelen
- `Terminated` - Leállítva

---

## 🔐 Autentikáció

Összes API: `authLevel: anonymous` (jelenleg)

**Javaslat**: Éles környezetben állítsd `function` vagy `admin` szintre

---

## 📊 HTTP Status Kódok

| Kód | Leírás |
|-----|--------|
| 200 | OK |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

## 🔗 Teljes Dokumentáció

- **IMPLEMENTATION.md** - Implementáció leírása
- **TESTING.md** - Tesztelési útmutató
- **Solution architecture.md** - Teljes architektúra

