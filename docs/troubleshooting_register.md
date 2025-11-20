# Troubleshooting Register - Integration Test Failure

## Objective
Run `tests/test_integration.py` successfully.

## Current Status
Failing with `ConnectionRefusedError` on `localhost:7071`. Backend fails to connect to Storage Emulator (`localhost:10000`).

## Failed Attempts Register

| Attempt ID | Strategy | Outcome | Analysis |
| :--- | :--- | :--- | :--- |
| **1** | Start Azurite (bg) -> Start Func (bg) -> Run Test | **Failed** | `ConnectionRefusedError`. Func could not connect to Azurite. |
| **2** | Install missing pip reqs -> Start Func -> Run Test | **Failed** | `ModuleNotFoundError` (azure.data, google.oauth2). Func crashed. |
| **3** | Fix `requirements.txt` -> Start Func -> Run Test | **Failed** | `ingestion_timer` failed. `ConnectionRefusedError` persisted. |
| **4** | Downgrade `protobuf` -> Start Func -> Run Test | **Failed** | No change. Connection refused. |
| **5** | `Start-Process` (detached) for Azurite | **Failed** | Port 10000 never opened. Process likely died immediately. |
| **6** | `azurite --debug` (bg) | **Failed** | Logs showed Azurite starting and immediately closing. |
| **7** | `azurite --inMemoryPersistence` (bg) | **Failed** | Process started and immediately closed. Suspect terminal session closure. |
| **8** | `Start-Job` with incompatible flags | **Failed** | Error: `--inMemoryPersistence` not supported with `--location`. |

## Next Strategy (Attempt 9)
**Hypothesis**: Azurite is failing to persist or crashing due to file system issues in the current `.azurite` folder.
**Plan**:
1. Kill all related processes (`node`, `func`, `python`).
2. Start Azurite with `--inMemoryPersistence` to bypass disk I/O issues.
3. Verify port 10000 is open.
4. Start Azure Functions.
5. Verify port 7071 is open.
6. Run Integration Test.
