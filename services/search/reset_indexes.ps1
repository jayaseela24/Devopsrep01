param(
    [string]$environment = $(throw "-environment is required"),
    [string]$encription = $(throw "-encription is required")
)

# #########################################################################
# Befode execute make sure you are under the ./services/search directory
# To execute use:
# .\reset_indexes.ps1 -environment STL -encription true
# #########################################################################

$JSON_PATH = ".\jsons"
# $JSON_PATH = ".\jsons\test"

Write-Host "Reseting indexes for environment: ${environment}"

$environments = Get-Content ".\jsons\environment_details.json" | ConvertFrom-Json 
foreach ($env_item in $environments){
    if($env_item.name -eq $environment){
        $envi = $env_item
        break
    }
}
Write-Host "Loaded environment details: " $envi.name
$apikey = $envi.AISearch_key_secret
$apikey_secret = $envi.AISearch_key_secret
$vault_name = $envi.kv_vault_name
$subscription = $envi.subscription
$cloud = $envi.azure_cloud

az cloud set --name "$cloud"
# az login
Write-Host "Setting subscription: " $subscription
az account set --subscription "$subscription" # confure it accordingly

#get API key
Write-Host "Getting AI Search API key...: ${vault_name} > ${apikey_secret}"
$apikey = az keyvault secret show --name "${apikey_secret}" --vault-name "${vault_name}" --query "value" -o tsv
Write-Host "Got Search API key: " + $apikey.substring(0, 5) + "*******"
$headers = @{
    'api-key' = "${apikey}"
    'Content-Type' = 'application/json' 
    'Accept' = 'application/json' 
}

$indexes = @(
    'index_ngentity-accountinfo-index-4.json',
    'index_ngentity-accountinfoskill-index-1.json',
    'index_ngentity-entityinfo-index-4.json',
    'index_ngentity-entityinfoskill-index-1.json'
)

Write-Host "----------------------------------"
Write-Host " RECREATING THE INDEXES           "
Write-Host "----------------------------------"

ForEach($index in $indexes){
    $index_name = $index.Replace('index_','')
    $index_name = $index_name.Replace('.json','')
    $index_file_name = $index
    $ai_search_endpoint = $envi.AIsearch_endpoint
    Write-Host "----------------------------------"
    Write-Host " Processing " $index_name
    Write-Host "----------------------------------"

    #delete index
    $url = "${ai_search_endpoint}/indexes/${index_name}?api-version=2023-10-01-preview"
    Write-Host "DELETE ${index_name} -> ${url}"
    Invoke-RestMethod -Uri $url -Headers $headers -Method Delete | ConvertTo-Json

    # recreate index
    $body = $body = Get-Content "$($JSON_PATH)\$($index_file_name)" | ConvertFrom-Json 

    # add encryption details
    if($encription -like 'true'){
        $client_id_secret_name = $envi.encription_access_creds_client_id
        $client_id = az keyvault secret show --name "${client_id_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
        Write-Host "Using app registration client id: " + $client_id
        $client_secret_secret_name =  $envi.encription_access_creds_client_secret
        $client_secret = az keyvault secret show --name "${client_secret_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
        Write-Host "Using app registration secret: " + $client_secret.substring(0,5) + "********"
        $body.encryptionKey = @{}
        $body.encryptionKey.keyVaultKeyName = $envi.encription_kv_keyname
        $body.encryptionKey.keyVaultKeyVersion = $envi.encription_kv_keyversion
        $body.encryptionKey.keyVaultUri = $envi.encription_kv_uri
        $body.encryptionKey.accessCredentials = @{}
        $body.encryptionKey.accessCredentials.applicationId = $client_id
        $body.encryptionKey.accessCredentials.applicationSecret = $client_secret
    }

    $url = "${ai_search_endpoint}/indexes/${index_name}?api-version=2023-10-01-preview"
    Write-Host "CREATE ${index_name} -> ${url}"

    # create/update the index
    $body = $body | ConvertTo-Json -depth 32
    # Write-host "Body: " $body
    Invoke-RestMethod -Uri $url -Headers $headers -Method Put -Body $body | ConvertTo-Json
    Start-Sleep -Seconds 1.5
}


Write-Host "----------------------------------"
Write-Host " RESETING THE INDEXES           "
Write-Host "----------------------------------"


$indexers = @(
    'indexer_ngentity-accountinfo-index-4-sql-indexer-1.json',
    'indexer_ngentity-accountinfoskill-indexer-1.json',
    'indexer_ngentity-entityinfo-index-4-sql-indexer-1.json',
    'indexer_ngentity-entityinfoskill-indexer-1.json'
)

ForEach($indexer in $indexers){
    $indexer_name = $indexer.Replace('indexer_','')
    $indexer_name = $indexer_name.Replace('.json','')
    $ai_search_endpoint = $envi.AIsearch_endpoint

    #delete index
    $url = "${ai_search_endpoint}/indexers/${indexer_name}/reset?api-version=2023-10-01-preview"
    Write-Host "RESET ${indexer_name} -> ${url}"
    Invoke-RestMethod -Uri $url -Headers $headers -Method Post | ConvertTo-Json

    Start-Sleep -Seconds 1.5
}

