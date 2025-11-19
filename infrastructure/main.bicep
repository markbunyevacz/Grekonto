@description('The name of the environment (e.g. "dev", "prod")')
param environmentName string = 'dev'

@description('The location of the resources')
param location string = resourceGroup().location

var resourceSuffix = uniqueString(resourceGroup().id)
var storageAccountName = 'stgrekonto${environmentName}${resourceSuffix}'
var keyVaultName = 'kv-grekonto-${environmentName}-${resourceSuffix}'
var functionAppName = 'func-grekonto-${environmentName}-${resourceSuffix}'
var appServicePlanName = 'asp-grekonto-${environmentName}-${resourceSuffix}'
var appInsightsName = 'appi-grekonto-${environmentName}-${resourceSuffix}'
var formRecognizerName = 'cog-grekonto-${environmentName}-${resourceSuffix}'
var staticWebAppName = 'stapp-grekonto-${environmentName}-${resourceSuffix}'

// 1. Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource rawContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'raw-documents'
}

resource processedContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'processed-documents'
}

// 2. Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: [] // Access policies will be managed via RBAC or added later
    enableRbacAuthorization: true
  }
}

// 3. Azure AI Document Intelligence
resource formRecognizer 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: formRecognizerName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'FormRecognizer'
  properties: {
    customSubDomainName: formRecognizerName
  }
}

// 4. Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// 5. App Service Plan (Consumption)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {}
}

// 6. Azure Function App
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.10' // Using Python 3.10
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'FORM_RECOGNIZER_ENDPOINT'
          value: formRecognizer.properties.endpoint
        }
        {
          name: 'FORM_RECOGNIZER_KEY'
          value: formRecognizer.listKeys().key1
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
      ]
    }
  }
}

// 7. Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/Grekonto/grekonto-ai' // Placeholder
    branch: 'main'
    provider: 'GitHub'
  }
}

output storageAccountName string = storageAccountName
output functionAppName string = functionAppName
output staticWebAppName string = staticWebAppName
