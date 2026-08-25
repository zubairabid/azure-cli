# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from azure.mgmt.recoveryservices.models import SecuritySettings, SoftDeleteSettings, Vault, VaultProperties

from azure.cli.command_modules.backup.custom import update_vault
from azure.cli.command_modules.backup.custom_base import _get_raw_backup_resource, set_item_source_scan_configuration


class BackupCustomTest(unittest.TestCase):

    @patch('azure.cli.command_modules.backup.custom_base.send_raw_request')
    def test_get_raw_backup_resource_preserves_source_scan_and_threat_info(self, send_raw_request):
        payload = {
            "properties": {
                "sourceSideScanInfo": {
                    "sourceSideScanStatus": "Configured",
                    "sourceSideScanSummary": "Healthy"
                },
                "threatStatus": "UnHealthy",
                "threatInfo": [{"threatTitle": "Test threat", "threatSeverity": "High"}]
            }
        }
        send_raw_request.return_value = SimpleNamespace(json=Mock(return_value=payload))
        cmd = SimpleNamespace(cli_ctx=SimpleNamespace(
            cloud=SimpleNamespace(endpoints=SimpleNamespace(
                resource_manager="https://management.azure.com/"
            ))
        ))

        result = _get_raw_backup_resource(cmd, "/subscriptions/subscription/resource", "resource-group")

        self.assertEqual("Configured", result['properties']['sourceSideScanInfo']['sourceSideScanStatus'])
        self.assertEqual("UnHealthy", result['properties']['threatStatus'])
        self.assertEqual("High", result['properties']['threatInfo'][0]['threatSeverity'])
        self.assertEqual("resource-group", result['resourceGroup'])
        self.assertTrue(send_raw_request.call_args.args[2].endswith("?api-version=2026-07-01"))

    def test_update_vault_sets_source_scan_state(self):
        soft_delete_settings = SoftDeleteSettings(soft_delete_state="Enabled")
        existing_vault = Vault(
            location="eastus",
            properties=VaultProperties(
                security_settings=SecuritySettings(soft_delete_settings=soft_delete_settings)
            )
        )

        for state in ("Enabled", "Disabled"):
            with self.subTest(state=state):
                client = Mock()
                client.get.return_value = existing_vault

                update_vault(
                    Mock(), client, "vault", "resource-group", source_scan_state=state
                )

                patch_vault = client.begin_update.call_args.args[2]
                source_scan_configuration = patch_vault.properties.security_settings.source_scan_configuration
                self.assertEqual(state, source_scan_configuration.state)
                self.assertIsNone(source_scan_configuration.source_scan_identity)
                self.assertIs(
                    soft_delete_settings,
                    patch_vault.properties.security_settings.soft_delete_settings
                )

    @patch('azure.cli.command_modules.backup.custom_base.get_subscription_id', return_value='subscription')
    @patch('azure.cli.command_modules.backup.custom_base.send_raw_request')
    @patch('azure.cli.command_modules.backup.custom_base.show_item')
    def test_set_item_source_scan_configuration(self, show_item, send_raw_request, _):
        item = SimpleNamespace(
            id=("/subscriptions/subscription/resourceGroups/resource-group/providers/"
                "Microsoft.RecoveryServices/vaults/vault/backupFabrics/Azure/"
                "protectionContainers/iaasvmcontainer;iaasvmcontainerv2;rg;vm/"
                "protectedItems/vm;iaasvmcontainerv2;rg;vm"),
            properties=SimpleNamespace(backup_management_type="AzureIaasVM")
        )
        show_item.return_value = item
        send_raw_request.return_value = SimpleNamespace(
            text="",
            headers={
                "Azure-AsyncOperation": "https://management.azure.com/operations/status",
                "Location": "https://management.azure.com/operations/result",
                "Retry-After": "60"
            }
        )
        cmd = SimpleNamespace(cli_ctx=SimpleNamespace(
            cloud=SimpleNamespace(endpoints=SimpleNamespace(
                resource_manager="https://management.azure.com/"
            ))
        ))

        result = set_item_source_scan_configuration(
            cmd, Mock(), "resource-group", "vault", "vm", "vm", "Enabled", "AzureIaasVM", "VM"
        )

        request_url = send_raw_request.call_args.args[2]
        self.assertIn("/protectionContainers/iaasvmcontainer%3Biaasvmcontainerv2%3Brg%3Bvm/", request_url)
        self.assertIn("/protectedItems/vm%3Biaasvmcontainerv2%3Brg%3Bvm/configureSourceScan", request_url)
        self.assertTrue(request_url.endswith("?api-version=2026-07-01"))
        self.assertEqual('{"sourceScanAction": "Enable"}', send_raw_request.call_args.kwargs['body'])
        self.assertEqual("Accepted", result['status'])
        self.assertEqual("https://management.azure.com/operations/status", result['azureAsyncOperation'])

    @patch('azure.cli.command_modules.backup.custom_base.get_subscription_id', return_value='subscription')
    @patch('azure.cli.command_modules.backup.custom_base.send_raw_request')
    @patch('azure.cli.command_modules.backup.custom_base.show_item')
    def test_set_item_source_scan_configuration_returns_operation_status(self, show_item, send_raw_request, _):
        show_item.return_value = SimpleNamespace(
            id=("/subscriptions/subscription/resourceGroups/resource-group/providers/"
                "Microsoft.RecoveryServices/vaults/vault/backupFabrics/Azure/"
                "protectionContainers/container/protectedItems/item"),
            properties=SimpleNamespace(backup_management_type="AzureIaasVM")
        )
        send_raw_request.return_value = SimpleNamespace(
            text='{"status": "Succeeded"}',
            json=Mock(return_value={"status": "Succeeded"})
        )
        cmd = SimpleNamespace(cli_ctx=SimpleNamespace(
            cloud=SimpleNamespace(endpoints=SimpleNamespace(
                resource_manager="https://management.azure.com"
            ))
        ))

        result = set_item_source_scan_configuration(
            cmd, Mock(), "resource-group", "vault", "container", "item", "Disabled", "AzureIaasVM", "VM"
        )

        self.assertEqual('{"sourceScanAction": "Disable"}', send_raw_request.call_args.kwargs['body'])
        self.assertEqual({"status": "Succeeded"}, result)


if __name__ == '__main__':
    unittest.main()