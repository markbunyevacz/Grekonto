# Troubleshooting Register - Integration Test Failure

## Objective
Run `tests/test_integration.py` successfully.

## Current Status
Failing with `ConnectionRefusedError` on `localhost:7071`. Azurite port conflict (10000) was resolved, but Backend (7071) is still not reachable during tests.

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
| **9** | Kill processes -> Restart Azurite -> Start Func | **Failed** | Port 10000 was `EADDRINUSE`. Killed blocking process. Azurite started. Func started but tests failed with `ConnectionRefused`. |
| **10** | Check Port 7071 | **Failed** | `netstat` shows 7071 is NOT listening even after `func start`. Func process might be exiting or hanging. |
| **11** | `func start --verbose` | **Partial Success** | Host started successfully (logs confirmed). `ingestion_timer` ran. However, environment was cluttered with too many terminals, leading to confusion and potential zombie processes. |
| **12** | Clean Slate -> Restart Azurite/Func -> Run Test | **Failed (Test Runner)** | Backend started and is listening on 7071. Test execution failed with `ModuleNotFoundError` because `python -m unittest tests/test_integration.py` is invalid syntax for module discovery from `backend` dir. |
| **13** | `python -m unittest tests.test_integration` | **Failed** | `ModuleNotFoundError`. Likely due to missing `__init__.py` in `tests` folder or `sys.path` issues. |
| **14** | `python tests/test_integration.py` | **Failed (Assertion)** | Test ran! Backend reachable. Failed with 500: `Connection string missing required connection details`. |
| **15** | Check Azurite -> Add Logging -> Rerun | **Failed** | Azurite is running. Test failed with same error. Need to restart backend to ensure logging code is active and visible. |
| **16** | Restart Backend (bg) -> Run Test | **Failed (500)** | Test failed. Backend running. Need to inspect logs for debug output. |
| **17** | Retrieve Logs | **Failed** | Logs retrieved but didn't show request processing (likely buffering or truncated). Test still failing. |
| **18** | Hardcode Conn String + Print | **Failed (500)** | Test failed. `ingestion_timer` works (connects to Azurite). Need to fetch logs to see `print` output. |
| **19** | Analyze Logs | **Failed** | Logs retrieved. `ingestion_timer` logs visible. `api_upload_document` logs **MISSING**. Test got 500. |

## Next Strategy (Attempt 20)
**Hypothesis**: The 500 error occurs before the function code runs (e.g., binding error), or logs are suppressed.
**Plan**:
1.  Inspect `backend/api_upload_document/function.json`.
2.  Add `print("DEBUG: api_upload_document hit")` at the very top of `backend/api_upload_document/__init__.py`.
3.  Restart Backend -> Run Test -> Fetch Logs.
