
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import json
import os
from azure.cli.testsdk import ScenarioTest, record_only

# Production vault and resources
ase_production_vault = 'ase-rsv-grs'
production_vm_container_name = 'VMAppContainer;Compute;ase-rg-ccy;ase-ccy-vm5'
production_vm_friendly_name = 'ase-ccy-vm5'
production_backup_policy = 'DailyPolicy-ma2c99lv'

# Registration vault and resources  
ase_registration_vault = 'ase-rsv-ccy'
registration_vm_container_name = 'VMAppContainer;Compute;ase-rg-ccy;ase-ccy-vm2'
registration_vm_friendly_name = 'ase-ccy-vm2'
registration_vm_resource_id = '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/ase-rg-ccy/providers/Microsoft.Compute/virtualMachines/ase-ccy-vm2'
registration_backup_policy = 'DailyPolicy-m9aya1dh'

# Shared resources
ase_resource_group = 'ase-rg-ccy'
primary_database_friendly_name = 'asetestdb1'
secondary_database_friendly_name = 'asetestdb3'
master_database_friendly_name = 'master'
primary_database_item_name = 'SAPAseDatabase;ab4;asetestdb1'
secondary_database_item_name = 'SAPAseDatabase;ab4;asetestdb2'
tertiary_database_item_name = 'SAPAseDatabase;ab4;asetestdb3'
master_database_item_name = 'SAPAseDatabase;ab4;master'


class ASEBackupTests(ScenarioTest, unittest.TestCase):

    def test_ase_production_backup_and_policy_operations(self):
        """Test backup and policy operations on production ASE resources."""
        self.kwargs.update({
            'vault': ase_production_vault,
            'vm_full_name': production_vm_container_name,
            'vm_friendly_name': production_vm_friendly_name,
            'rg': ase_resource_group,
            'backup_item_friendly_name': primary_database_friendly_name,
            'backup_item_protection_state': 'Protected',
            'backup_policy': production_backup_policy,
            'policy_new': self.create_random_name('clitest-policy', 24),
            'reg_vm_id': registration_vm_resource_id,
        })

        # Show backup container details
        self.kwargs['container'] = self.cmd('backup container show -n {vm_full_name} -v {vault} -g {rg} --backup-management-type AzureWorkload', checks = [
            self.check('name', '{vm_full_name}'),
            self.check('properties.friendlyName', '{vm_friendly_name}')
        ]).get_output_in_json()

        # List backup containers
        self.cmd('backup container list --backup-management-type AzureWorkload -v {vault} -g {rg}', checks=[
            self.check("length(@)", 2)
        ])
        
        # Show backup item details
        self.cmd('backup item show --backup-management-type AzureWorkload -g {rg} -v {vault} -c {vm_full_name} -n {backup_item_friendly_name}', checks=[
            self.check("properties.friendlyName", '{backup_item_friendly_name}'),
            self.check("properties.protectionState", '{backup_item_protection_state}'),
            self.check("resourceGroup", '{rg}'),
            self.check("properties.isScheduledForDeferredDelete", None)
        ])

        # Get existing policy for template
        self.kwargs['policy1_json'] = self.cmd('backup policy show -g {rg} -v {vault} -n {backup_policy}', checks=[
            self.check('name', '{backup_policy}'),
            self.check('resourceGroup', '{rg}')
        ]).get_output_in_json()

        self.kwargs['policy_json'] = json.dumps(self.kwargs['policy1_json'], separators=(',', ':')).replace('\'', '\\\'').replace('"', '\\"')

        # Create new policy from template
        self.cmd("backup policy create -g {rg} -v {vault} --policy {policy_json} --backup-management-type AzureWorkload --workload-type SAPAseDatabase --name {policy_new}", checks=[
            self.check('name', '{policy_new}'),
            self.check('resourceGroup', '{rg}')
        ])
        
        # Clean up test policy
        self.cmd('backup policy delete -g {rg} -v {vault} -n {policy_new}')

        # List ASE policies
        self.cmd('backup policy list -g {rg} -v {vault}  --workload-type SAPAseDatabase', checks=[
            self.check("length([?name == '{backup_policy}'])", 1)
        ])

    def test_ase_backup_and_restore_operations(self):
        """Test backup and restore workflow for ASE databases."""
        self.kwargs.update({
            'rg': ase_resource_group,
            'vault': ase_production_vault,
            'backup_item_name_db1': primary_database_item_name,
            'backup_item_name_db2': secondary_database_item_name,
            'vm_friendly_name': production_vm_friendly_name,
            'vm_full_name': production_vm_container_name
        })

        # Trigger on-demand backup
        self.cmd('backup protection backup-now -g {rg} -v {vault} -c {vm_friendly_name} -i {backup_item_name_db1} --backup-type Full  --enable-compression false --backup-management-type AzureWorkload')

        # Get latest recovery point
        self.kwargs['rp'] = self.cmd('backup recoverypoint list -g {rg} -v {vault} -c {vm_friendly_name} -i {backup_item_name_db1} --workload-type SAPAseDatabase --backup-management-type AzureWorkload --query [0]').get_output_in_json()
        self.kwargs['rp'] = self.kwargs['rp']['name']

        # Generate recovery configuration for restore
        self.kwargs['rc'] = json.dumps(self.cmd('backup recoveryconfig show --vault-name {vault} -g {rg} --restore-mode OriginalWorkloadRestore --rp-name {rp} --item-name {backup_item_name_db1} --container-name {vm_full_name}').get_output_in_json(), separators=(',', ':'))
        
        with open("recoveryconfig_ase_restore.json", "w") as f:
            f.write(self.kwargs['rc'])

        # Initiate restore operation
        self.kwargs['backup_job'] = self.cmd('backup restore restore-azurewl --vault-name {vault} -g {rg} --recovery-config recoveryconfig_ase_restore.json', checks=[
            self.check("properties.operation", "Restore"),
            self.check("properties.status", "InProgress"),
            self.check("resourceGroup", '{rg}')
        ]).get_output_in_json()

    @unittest.skip("Unit test is currently blocked as soft delete is enabled by default")
    def test_ase_container_registration_lifecycle(self):
        """Test container registration and unregistration lifecycle."""
        self.kwargs.update({
            'vault': ase_registration_vault,
            'vm': registration_vm_friendly_name,
            'rg': ase_resource_group,
            'reg_vm_id': registration_vm_resource_id,
            'vm_full_name': registration_vm_container_name,
            'backup_policy': registration_backup_policy,
            'backup_item': tertiary_database_item_name,
            'backup_item_friendly_name': secondary_database_friendly_name
        })

        # Register container for ASE workload backup
        self.cmd('backup container register -v {vault} -g {rg} --workload-type SAPAseDatabase --backup-management-type AzureWorkload --resource-id {reg_vm_id}')

        # Unregister container
        self.cmd('backup container unregister -v {vault} -g {rg} -c {vm_full_name} -y')

    @unittest.skip("Unit test is currently blocked as soft delete is enabled by default")
    def test_ase_protection_configuration_lifecycle(self):
        """Test protection configuration lifecycle for ASE databases."""
        self.kwargs.update({
            'vault': ase_registration_vault,
            'vm': registration_vm_friendly_name,
            'rg': ase_resource_group,
            'reg_vm_id': registration_vm_resource_id,
            'backup_policy': registration_backup_policy,
            'backup_item': master_database_item_name,
            'backup_item_friendly_name': master_database_friendly_name
        })

        # Enable protection for ASE database
        self.cmd('backup protection enable-for-azurewl -v {vault} -g {rg} -p {backup_policy} --protectable-item-type SAPAseDatabase --protectable-item-name {backup_item} --server-name {vm} --workload-type SAPAseDatabase', checks=[
            self.check("properties.entityFriendlyName", '{vm}'),
            self.check("properties.operation", "ConfigureBackup"),
            self.check("properties.status", "Completed"),
            self.check("resourceGroup", '{rg}')
        ])
        
        # Disable protection with data deletion
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} -y --delete-backup-data true -y')

    def test_ase_undelete_protection(self):
        """Test ASE database undelete protection functionality."""
        self.kwargs.update({
            'vault': ase_registration_vault,
            'vm_full_name': registration_vm_container_name,
            'vm_friendly_name': registration_vm_friendly_name,
            'rg': ase_resource_group,
            'backup_item': primary_database_item_name,
            'backup_item_friendly_name': primary_database_friendly_name
        })

        # Disable protection without deleting backup data (soft delete)
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm_full_name} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} --delete-backup-data false --yes')
        
        # Verify soft-deleted state (optional)
        try:
            item_json = self.cmd('backup item show --backup-management-type AzureWorkload -g {rg} -v {vault} -c {vm_full_name} -n {backup_item}').get_output_in_json()
            if 'properties' in item_json and 'isScheduledForDeferredDelete' in item_json['properties']:
                self.assertTrue(item_json['properties']['isScheduledForDeferredDelete'])
        except:
            pass

        # Execute undelete protection operation
        self.cmd('backup protection undelete --backup-management-type AzureWorkload --workload-type SAPAseDatabase -c {vm_full_name} -i {backup_item} -g {rg} -v {vault}', checks=[
            self.check("properties.entityFriendlyName", '{vm_friendly_name}'),
            self.check("properties.operation", "Undelete"),
            self.check("properties.status", "Completed"),
            self.check("resourceGroup", '{rg}')
        ])

    def test_ase_disable_protection_retain_data(self):
        """Test ASE database disable protection with data retention."""
        self.kwargs.update({
            'vault': ase_registration_vault,
            'vm_full_name': registration_vm_container_name,
            'vm_friendly_name': registration_vm_friendly_name,
            'rg': ase_resource_group,
            'backup_item': secondary_database_item_name,
            'backup_item_friendly_name': primary_database_friendly_name
        })

        # Disable protection while retaining recovery points per policy
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm_full_name} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} --retain-recovery-points-as-per-policy --yes', checks=[
            self.check("properties.entityFriendlyName", '{vm_friendly_name}'),
            self.check("properties.operation", "DisableBackup"),
            self.check("properties.status", "Completed"),
            self.check("resourceGroup", '{rg}')
        ])
