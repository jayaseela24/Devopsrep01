import os
import json

# edit the following variables
services = os.environ.get('SERVICES', '')
print('SERVICES: ', services)
if len(services.strip()) == 0:
    print('parameter SERVICES is required')
    quit()

environment = os.environ.get('ENVIRONMENT', '')
print('ENVIRONMENT: ', environment)
if len(environment.strip()) == 0:
    print('parameter ENVIRONMENT is required')
    quit()

override_same_version = os.environ.get('OVERRIDE_SAME_VERSION', 'false')
print('OVERRIDE_SAME_VERSION: ', override_same_version)


services_to_deploy_response = {
    "AKS": [],
    "function_apps_dotnet": [],
    "function_apps_python": [],
    "sink_object": [],
    "spa_client_side": [],
    "spa_server_side": [],
    "smoke_test": [],
    "nosql_migrations": []
}

services_array = json.loads(services.replace('\'','"'))
for service in services_array:
    service_name = service["service_name"]
    source_version = service["source_version"]
    target_version = service["target_version"]
    if source_version == target_version and override_same_version == 'false':
        print(f'\t >> skipping service: {service_name}')
    else:
        print(f'service: {service_name}')
        services_config = open(f"./deployment_files/services/{service_name}.json", "r")
        services_config_json = json.load(services_config)
        if "AKS" in services_config_json:
            for aks in services_config_json["AKS"]:
                if environment in aks:
                    aks_data = aks[ environment ]
                    aks_data["service_name"] = service_name
                    aks_data["target_version"] = target_version
                    services_to_deploy_response["AKS"].append(aks_data)
        if "function_apps_dotnet" in services_config_json:
            for fapp in services_config_json["function_apps_dotnet"]:
                if environment in fapp:
                    fapp_data = fapp[ environment ]
                    fapp_data["service_name"] = service_name
                    fapp_data["target_version"] = target_version
                    services_to_deploy_response["function_apps_dotnet"].append( fapp_data )
        if "function_apps_python" in services_config_json:
            for fapp in services_config_json["function_apps_python"]:
                if environment in fapp:
                    fapp_data = fapp[ environment ]
                    fapp_data["service_name"] = service_name
                    fapp_data["target_version"] = target_version
                    services_to_deploy_response["function_apps_python"].append(fapp_data)
        if "sink_object" in services_config_json:
            for sinkobj in services_config_json["sink_object"]:
                if environment in sinkobj:
                    services_to_deploy_response["sink_object"].append(sinkobj[ environment ])
        if "spa_client_side" in services_config_json:
            for spaclientside in services_config_json["spa_client_side"]:
                if environment in spaclientside:
                    spaclientside_data = spaclientside[ environment ]
                    spaclientside_data["service_name"] = service_name
                    spaclientside_data["target_version"] = target_version
                    spaclientside_data["target_version_number"] = target_version.replace('v','')
                    services_to_deploy_response["spa_client_side"].append(spaclientside_data)
        if "spa_server_side" in services_config_json:
            for spaserverside in services_config_json["spa_server_side"]:
                if environment in spaserverside:
                    spaserverside_data = spaserverside[ environment ]
                    spaserverside_data["service_name"] = service_name
                    spaserverside_data["target_version"] = target_version
                    spaserverside_data["target_version_number"] = target_version.replace('v','')
                    services_to_deploy_response["spa_server_side"].append(spaserverside_data)
        if "smoke_test" in services_config_json:
            if services_config_json["smoke_test"] != None and environment in services_config_json["smoke_test"]:
                services_to_deploy_response["smoke_test"].append(services_config_json["smoke_test"][ environment ])
        if "nosql_migrations" in services_config_json:
            for mongomigration in services_config_json["nosql_migrations"]:
                if environment in mongomigration:
                    mongomigration_data = mongomigration[ environment ]
                    mongomigration_data["service_name"] = service_name
                    mongomigration_data["target_version"] = target_version
                    services_to_deploy_response["nosql_migrations"].append(mongomigration_data)

response = json.dumps(services_to_deploy_response)
print(response)

# with open("Output2.txt", "w") as text_file:
#     text_file.write(response)

print(f'::set-output name=deployment_data_array::{response}')


# Filter services with different version and SQL scripts
print("\nFilter services with different version and SQL scripts")
print("=========================================================")
# with open("services_sql_1.txt", "w") as text_file:
#     text_file.write(json.dumps(services_array, indent=4))

sql_services_array = []
for service in services_array:
    service_name = service["service_name"]
    source_version = service["source_version"]
    target_version = service["target_version"]
    if source_version == target_version and override_same_version == 'false':
        print(f'\t >> skipping service: {service_name}')
    else:
        print(f'service: {service_name}')
        sql_config = open(f"./Actions/revx-services-deployment/services_sql_script_mapping.json", "r")
        sql_config_json = json.load(sql_config)
        services_with_sql = [ x["service_name"] for x in sql_config_json["services"] if len(x["fd_scripts"]) + len(x["migration_scripts"]) > 0]
        if service_name in services_with_sql:
            print(f'service: {service_name}')
            sql_services_array.append(service)

# with open("services_sql_2.txt", "w") as text_file:
#     text_file.write(json.dumps(sql_services_array, indent=4))

sql_services_array_response = json.dumps(sql_services_array)
print(sql_services_array_response)
print(f'::set-output name=sql_services_array::{sql_services_array_response}')