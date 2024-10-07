#!/usr/bin/env python
import json
from pathlib import Path
from regscale.core.app.application import Application
from regscale.core.app.api import Api
from regscale.models.regscale_models.file import File

app = Application()
api = Api()


def get_file_info():
    global existing_files, file_id, res
    # Get existing files for the parent
    existing_files = File.get_files_for_parent_from_regscale(parent_id=17, parent_module='securityplans')
    # Check if the file already exists
    for file in existing_files:
        if file.trustedDisplayName == file_name:
            file_id = file.id
            break
    else:
        # If file doesn't exist, create a new one
        res = File.upload_file_to_regscale(api=api, file_name=template_path, parent_id=17,
                                           parent_module='securityplans')
        file_id = res['id']

    return file_id


if __name__ == '__main__':
    mapper = {}

    # Load the mapper file
    template_path = Path('./FedRAMP-POAM-Template.xlsx')
    mapper_path = Path('./mapper.json')

    with open(mapper_path, 'r') as f:
        mapper = json.load(f)

    file_name = template_path.name

    file_id = get_file_info()

    existing_uuid = "cd5ffcfe-c030-4639-8e48-38233bae81df"

    # Define the export payload
    payload = {
        "uuid": existing_uuid,
        "active": True,
        "isPublic": True,
        "version": "5",
        "name": file_name,
        "filesId": file_id,
        "description": "BMC FedRAMP v5 FedRAMP POAM Template",
        "exportConfig": ''
    }

    # Export orchestration
    url = f'{app.config["domain"]}/api/ExportOrchestration'
    if not existing_uuid:
        res = api.post(url, json=payload)
        existing_uuid = res.json()['uuid']
    export_res = api.get(f'{url}/byUuid/{existing_uuid}')

    export_data = export_res.json()
    export_uuid = export_data['uuid']
    export_id = export_data['id']

    # Update export config with mapper data
    full_url = f'{url}/UpdateExportConfig/{export_uuid}'
    res = api.put(full_url, json=mapper)

    if res.status_code == 200:
        print("Mapper file updated in platform successfully")

    # Initiate export for the security plan
    initiate_export_url = f'{app.config["domain"]}/api/exports/GenerateExport/{export_id}/ForSecurityPlan/{3}'
    final_res = api.get(initiate_export_url)

    print(final_res.content)
