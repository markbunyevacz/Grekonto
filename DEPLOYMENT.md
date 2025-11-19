# Grekonto Deployment Guide

This guide details how to deploy the Grekonto AI Matching solution to Azure and run it locally.

## Prerequisites

1.  **Azure CLI**: [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2.  **Azure Functions Core Tools**: [Install Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3.  **Node.js & npm**: Required for the Frontend.
4.  **Python 3.10+**: Required for the Backend.
5.  **Bicep CLI**: Included with Azure CLI usually, or install manually.

## 1. Infrastructure Deployment (Azure)

We use Azure Bicep to provision all resources (Storage, KeyVault, Document Intelligence, Function App, Static Web App).

1.  **Login to Azure:**
    ```bash
    az login
    ```

2.  **Create a Resource Group:**
    ```bash
    az group create --name rg-grekonto-poc --location westeurope
    ```

3.  **Deploy Resources:**
    Navigate to the `infrastructure` folder and run:
    ```bash
    cd infrastructure
    az deployment group create --resource-group rg-grekonto-poc --template-file main.bicep
    ```
    *Note: You may need to provide a unique `appName` parameter if the default is taken.*

4.  **Get Output Values:**
    After deployment, note down the `functionAppName`, `storageAccountName`, and `documentIntelligenceEndpoint` from the outputs.

## 2. Backend Configuration (Local)

1.  **Navigate to Backend:**
    ```bash
    cd backend
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\Activate     # Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Local Settings:**
    Copy `local.settings.example.json` to `local.settings.json` and fill in the values from your Azure deployment (or use the Azure Storage Emulator / Azurite).

    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsSecretStorageType": "files",
        "DOCUMENT_INTELLIGENCE_ENDPOINT": "<YOUR_ENDPOINT>",
        "DOCUMENT_INTELLIGENCE_KEY": "<YOUR_KEY>"
      }
    }
    ```

5.  **Run Locally:**
    ```bash
    func start
    ```
    The API will be available at `http://localhost:7071`.

## 3. Frontend Configuration (Local)

1.  **Navigate to Frontend:**
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Run Development Server:**
    ```bash
    npm run dev
    ```
    The frontend will proxy requests to `http://localhost:7071` (configured in `vite.config.ts`).

## 4. Production Deployment

### Backend
```bash
cd backend
func azure functionapp publish <YourFunctionAppName>
```

### Frontend
1.  Build the project:
    ```bash
    npm run build
    ```
2.  Deploy to Azure Static Web Apps (using SWA CLI or GitHub Actions).
    ```bash
    swa deploy dist --env production
    ```

## Troubleshooting

-   **CORS Errors:** If running locally, ensure `vite.config.ts` proxy is set up correctly. In production, configure CORS in the Azure Function App to allow the Static Web App URL.
-   **Missing Keys:** Ensure KeyVault references are correctly set up in the Function App Configuration if using KeyVault.
