param(
    [string]$environment = $(throw "-environment is required"),
    [string]$encription = $(throw "-encription is required"),
    [string]$indexes = $(throw "-indexes is required"),
    [string]$datasources = $(throw "-datasources is required"),
    [string]$indexers = $(throw "-indexers is required"),
    [string]$skillsets = $(throw "-skillsets is required")
)

# #########################################################################
# Befode execute make sure you are under the ./services/search directory
# To execute use:
# .\indexes.ps1 -environment STL -encription true -indexes false -datasources false -indexers false -skillsets false
# #########################################################################

$JSON_PATH = ".\jsons"
# $JSON_PATH = ".\jsons\test"

Write-Host "Creating AI Search resources for environment: ${environment}"

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
$sql_mi_connection_string = $envi.sql_mi_connectionstring
$search_mi = $envi.search_managed_instance_resource_id
$subscription = $envi.subscription
$cloud = $envi.azure_cloud

az cloud set --name "$cloud"
# az login
Write-Host "Setting subscription: " $subscription
az account set --subscription "$subscription" # confure it accordingly

#get API key
$apikey = az keyvault secret show --name "${apikey_secret}" --vault-name "${vault_name}" --query "value" -o tsv
Write-Host "Got Search API key: " + $apikey.substring(0, 5) + "*******"
$headers = @{
    'api-key' = "${apikey}"
    'Content-Type' = 'application/json' 
    'Accept' = 'application/json' 
}

if($indexes -like 'true'){
    Write-Host "----------------------------------"
    Write-Host " Processing Indexes...."
    Write-Host "----------------------------------"

    # Read all index files

    ForEach ($file in Get-ChildItem -path $JSON_PATH -filter *.json) {
        if($file.Name -like 'index_*'){
            Write-Host "Processing index..: " $file.Name

            # get index body
            $body = Get-Content "$($JSON_PATH)\$($file.Name)" | ConvertFrom-Json 

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

            $index_name = $body.name
            $ai_search_endpoint = $envi.AIsearch_endpoint
            $url = "${ai_search_endpoint}/indexes/${index_name}?api-version=2023-10-01-preview"
            Write-Host "Creating index: ${index_name} at ${url}"

            # create/update the index
            $body = $body | ConvertTo-Json -depth 32
            # Write-host "Body: " + $body
            Invoke-RestMethod -Uri $url -Headers $headers -Method Put -Body $body | ConvertTo-Json
            Start-Sleep -Seconds 1.5
        }
    }
}

if($datasources -like 'true'){
    Write-Host "----------------------------------"
    Write-Host " Processing Datasources...."
    Write-Host "----------------------------------"

    # Read all datasources
    ForEach ($file in Get-ChildItem -path $JSON_PATH  -filter *.json) {
        if($file.Name -like 'datasource_*'){
            Write-Host "Processing datasource..: " $file.Name

            # get index body
            $body = Get-Content "$($JSON_PATH)\$($file.Name)" | ConvertFrom-Json 

            # add encryption details
            if($encription -like 'true'){
                $client_id_secret_name = $envi.encription_access_creds_client_id
                $client_id = az keyvault secret show --name "${client_id_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $client_secret_secret_name =  $envi.encription_access_creds_client_secret
                $client_secret = az keyvault secret show --name "${client_secret_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $body.encryptionKey = @{}
                $body.encryptionKey.keyVaultKeyName = $envi.encription_kv_keyname
                $body.encryptionKey.keyVaultKeyVersion = $envi.encription_kv_keyversion
                $body.encryptionKey.keyVaultUri = $envi.encription_kv_uri
                $body.encryptionKey.accessCredentials = @{}
                $body.encryptionKey.accessCredentials.applicationId = $client_id
                $body.encryptionKey.accessCredentials.applicationSecret = $client_secret

                $body.credentials.connectionString = $sql_mi_connection_string
                $body.identity.userAssignedIdentity = $search_mi
            }

            $index_name = $body.name
            $ai_search_endpoint = $envi.AIsearch_endpoint
            $url = "${ai_search_endpoint}/datasources/${index_name}?api-version=2023-10-01-preview"
            Write-Host "Creating datasource: ${index_name} at ${url}"

            # create/update the index
            $body = $body | ConvertTo-Json -depth 32
            Invoke-RestMethod -Uri $url -Headers $headers -Method Put -Body $body | ConvertTo-Json
        }
    }
}

if($skillsets -like 'true'){
    Write-Host "----------------------------------"
    Write-Host " Processing Skillsets...."
    Write-Host "----------------------------------"

    # Read all skillsets
    ForEach ($file in Get-ChildItem -path $JSON_PATH -filter *.json) {
        if($file.Name -like 'skillset_*'){
            Write-Host "Processing skillset..: " $file.Name

            # get index body
            $body = Get-Content "$($JSON_PATH)\$($file.Name)" | ConvertFrom-Json 

            $skillset_uri = $envi.skillset."$($file.Name)"
            Write-Host "URI: " $skillset_uri

            $body.skills[0].uri = $skillset_uri

            # add encryption details
            if($encription -like 'true'){
                $client_id_secret_name = $envi.encription_access_creds_client_id
                $client_id = az keyvault secret show --name "${client_id_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $client_secret_secret_name =  $envi.encription_access_creds_client_secret
                $client_secret = az keyvault secret show --name "${client_secret_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $body.encryptionKey = @{}
                $body.encryptionKey.keyVaultKeyName = $envi.encription_kv_keyname
                $body.encryptionKey.keyVaultKeyVersion = $envi.encription_kv_keyversion
                $body.encryptionKey.keyVaultUri = $envi.encription_kv_uri
                $body.encryptionKey.accessCredentials = @{}
                $body.encryptionKey.accessCredentials.applicationId = $client_id
                $body.encryptionKey.accessCredentials.applicationSecret = $client_secret
            }

            $skillset_name = $body.name
            $ai_search_endpoint = $envi.AIsearch_endpoint
            $url = "${ai_search_endpoint}/skillsets('${skillset_name}')?api-version=2023-10-01-preview"
            Write-Host "Creating skillset: ${skillset_name} at ${url}"

            # create/update the index
            $body = $body | ConvertTo-Json -depth 32
            Write-Host $body
            Invoke-RestMethod -Uri $url -Headers $headers -Method Put -Body $body | ConvertTo-Json
        }
    }
}

if($indexers -like 'true'){
    Write-Host "----------------------------------"
    Write-Host " Processing Indexers...."
    Write-Host "----------------------------------"

    # Read all indexers
    ForEach ($file in Get-ChildItem -path $JSON_PATH -filter *.json) {
        if($file.Name -like 'indexer_*'){
            Write-Host "Processing indexer..: " $file.Name

            # get index body
            $body = Get-Content "$($JSON_PATH)\$($file.Name)" | ConvertFrom-Json 

            # add encryption details
            if($encription -like 'true'){
                $client_id_secret_name = $envi.encription_access_creds_client_id
                $client_id = az keyvault secret show --name "${client_id_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $client_secret_secret_name =  $envi.encription_access_creds_client_secret
                $client_secret = az keyvault secret show --name "${client_secret_secret_name}" --vault-name "${vault_name}" --query "value" -o tsv
                $body.encryptionKey = @{}
                $body.encryptionKey.keyVaultKeyName = $envi.encription_kv_keyname
                $body.encryptionKey.keyVaultKeyVersion = $envi.encription_kv_keyversion
                $body.encryptionKey.keyVaultUri = $envi.encription_kv_uri
                $body.encryptionKey.accessCredentials = @{}
                $body.encryptionKey.accessCredentials.applicationId = $client_id
                $body.encryptionKey.accessCredentials.applicationSecret = $client_secret
            }

            $index_name = $body.name
            $ai_search_endpoint = $envi.AIsearch_endpoint
            $url = "${ai_search_endpoint}/indexers/${index_name}?api-version=2023-10-01-preview"
            Write-Host "Creating indexer: ${index_name} at ${url}"

            # create/update the index
            $body = $body | ConvertTo-Json -depth 32
            Invoke-RestMethod -Uri $url -Headers $headers -Method Put -Body $body | ConvertTo-Json
        }
    }
}

