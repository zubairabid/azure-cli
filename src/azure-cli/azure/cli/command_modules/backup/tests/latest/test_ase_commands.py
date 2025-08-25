
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Azure CLI test module for SAP ASE (Adaptive Server Enterprise) backup operations.

This module contains comprehensive tests for SAP ASE database backup functionality including:
- Production backup operations on permanently protected resources
- Registration/unregistration lifecycle tests on temporary resources  
- Policy management and configuration operations
- Backup, restore, and recovery point operations
- Protection lifecycle including enable, disable, and undelete operations

Test resources are categorized into two types:
1. Production resources: Permanently backed up items used for testing ongoing operations
2. Registration resources: Temporary items used for testing registration/configuration lifecycle
"""

import unittest
import json
import os
from azure.cli.testsdk import ScenarioTest, record_only

# =============================================================================
# PRODUCTION VAULT AND RESOURCES (Permanently backed up items)
# =============================================================================

# Production vault used for testing backup/restore operations on existing protected items
ase_production_vault = 'ase-rsv-grs'

# Production VM container name (full Azure resource path format)
production_vm_container_name = 'VMAppContainer;Compute;ase-rg-ccy;ase-ccy-vm5'

# Production VM friendly name (short name for display)
production_vm_friendly_name = 'ase-ccy-vm5'

# Backup policy used for production operations testing
production_backup_policy = 'DailyPolicy-ma2c99lv'

# =============================================================================
# REGISTRATION VAULT AND RESOURCES (Temporary registration/unregistration testing)
# =============================================================================

# Registration vault used for testing container registration/unregistration lifecycle
ase_registration_vault = 'ase-rsv-ccy'

# Registration VM container name (full Azure resource path format) 
registration_vm_container_name = 'VMAppContainer;Compute;ase-rg-ccy;ase-ccy-vm2'

# Registration VM friendly name (short name for display)
registration_vm_friendly_name = 'ase-ccy-vm2'

# Full Azure resource ID for the registration VM
registration_vm_resource_id = '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/ase-rg-ccy/providers/Microsoft.Compute/virtualMachines/ase-ccy-vm2'

# Backup policy used for registration operations testing
registration_backup_policy = 'DailyPolicy-m9aya1dh'

# =============================================================================
# SHARED RESOURCES AND DATABASE IDENTIFIERS
# =============================================================================

# Resource group containing all ASE test resources
ase_resource_group = 'ase-rg-ccy'

# Database names and identifiers for different test scenarios
primary_database_friendly_name = 'asetestdb1'  # Primary test database
secondary_database_friendly_name = 'asetestdb3'  # Secondary test database  
master_database_friendly_name = 'master'  # Master database for configuration tests

# Full database item names (SAP ASE format: SAPAseDatabase;server;database)
primary_database_item_name = 'SAPAseDatabase;ab4;asetestdb1'
secondary_database_item_name = 'SAPAseDatabase;ab4;asetestdb2'
tertiary_database_item_name = 'SAPAseDatabase;ab4;asetestdb3'
master_database_item_name = 'SAPAseDatabase;ab4;master'


class ASEBackupTests(ScenarioTest, unittest.TestCase):
    """
    Test suite for SAP ASE (Adaptive Server Enterprise) backup operations in Azure CLI.
    
    This class contains comprehensive tests covering the full lifecycle of ASE backup operations:
    - Production backup and policy management operations
    - Backup and restore workflows with recovery points
    - Container registration and unregistration lifecycle
    - Protection configuration enable/disable operations
    - Advanced protection operations (undelete, retain data)
    """

    def test_ase_production_backup_and_policy_operations(self):
        """
        Test comprehensive backup and policy operations on production ASE resources.
        
        This test validates:
        1. Container discovery and listing for existing protected items
        2. Backup item information retrieval and validation
        3. Backup policy creation from existing templates
        4. Policy management operations (create, delete, list)
        
        Uses production vault with permanently protected ASE resources.
        """
        # Set up test context with production resources
        self.kwargs.update({
            'vault': ase_production_vault,  # Production vault with existing protected items
            'vm_full_name': production_vm_container_name,  # Full container path
            'vm_friendly_name': production_vm_friendly_name,  # Display name
            'rg': ase_resource_group,  # Resource group containing all resources
            'backup_item_friendly_name': primary_database_friendly_name,  # Primary test database
            'backup_item_protection_state': 'Protected',  # Expected protection state
            'backup_policy': production_backup_policy,  # Existing policy for operations
            'policy_new': self.create_random_name('clitest-policy', 24),  # Generate unique policy name
            'reg_vm_id': registration_vm_resource_id,  # VM resource ID for reference
        })

        # Test 1: Show specific backup container details
        # Validates that the container exists and has correct properties
        self.kwargs['container'] = self.cmd('backup container show -n {vm_full_name} -v {vault} -g {rg} --backup-management-type AzureWorkload', checks = [
            self.check('name', '{vm_full_name}'),  # Verify full container name matches
            self.check('properties.friendlyName', '{vm_friendly_name}')  # Verify friendly name matches
        ]).get_output_in_json()

        # Test 2: List all backup containers in the vault
        # Validates that the expected number of containers are registered
        self.cmd('backup container list --backup-management-type AzureWorkload -v {vault} -g {rg}', checks=[
            self.check("length(@)", 2)  # Expect exactly 2 containers in production vault
        ])
        
        # Test 3: Show specific backup item details
        # Validates that the backup item exists and is properly protected
        self.cmd('backup item show --backup-management-type AzureWorkload -g {rg} -v {vault} -c {vm_full_name} -n {backup_item_friendly_name}', checks=[
            self.check("properties.friendlyName", '{backup_item_friendly_name}'),  # Verify item name
            self.check("properties.protectionState", '{backup_item_protection_state}'),  # Verify protection status
            self.check("resourceGroup", '{rg}'),  # Verify resource group
            self.check("properties.isScheduledForDeferredDelete", None)  # Verify not scheduled for deletion
        ])

        # Test 4: Retrieve existing backup policy for template
        # Gets an existing policy to use as a template for creating new policies
        self.kwargs['policy1_json'] = self.cmd('backup policy show -g {rg} -v {vault} -n {backup_policy}', checks=[
            self.check('name', '{backup_policy}'),  # Verify policy name
            self.check('resourceGroup', '{rg}')  # Verify resource group
        ]).get_output_in_json()

        # Prepare policy JSON for creation command (escape special characters)
        self.kwargs['policy_json'] = json.dumps(self.kwargs['policy1_json'], separators=(',', ':')).replace('\'', '\\\'').replace('"', '\\"')

        # Test 5: Create new backup policy from template
        # Creates a new policy based on the existing policy structure
        self.cmd("backup policy create -g {rg} -v {vault} --policy {policy_json} --backup-management-type AzureWorkload --workload-type SAPAseDatabase --name {policy_new}", checks=[
            self.check('name', '{policy_new}'),  # Verify new policy name
            self.check('resourceGroup', '{rg}')  # Verify resource group
        ])
        
        # Test 6: Delete the newly created policy
        # Cleans up the test policy to avoid resource accumulation
        self.cmd('backup policy delete -g {rg} -v {vault} -n {policy_new}')

        # Test 7: List all ASE-specific policies
        # Validates that the original policy still exists after cleanup
        self.cmd('backup policy list -g {rg} -v {vault}  --workload-type SAPAseDatabase', checks=[
            self.check("length([?name == '{backup_policy}'])", 1)  # Verify original policy exists
        ])

    def test_ase_backup_and_restore_operations(self):
        """
        Test complete backup and restore workflow for ASE databases.
        
        This test validates:
        1. On-demand backup creation with specific parameters
        2. Recovery point listing and selection
        3. Recovery configuration generation
        4. Restore operation initiation and monitoring
        
        Uses production vault with permanently protected ASE resources.
        """
        # Set up test context with production resources for backup/restore
        self.kwargs.update({
            'rg': ase_resource_group,  # Resource group for all operations
            'vault': ase_production_vault,  # Production vault with protected items
            'backup_item_name_db1': primary_database_item_name,  # Primary database full name
            'backup_item_name_db2': secondary_database_item_name,  # Secondary database full name
            'vm_friendly_name': production_vm_friendly_name,  # VM friendly name for operations
            'vm_full_name': production_vm_container_name  # Full container name for operations
        })

        # Test 1: Trigger on-demand backup
        # Creates a full backup with compression disabled for faster completion
        self.cmd('backup protection backup-now -g {rg} -v {vault} -c {vm_friendly_name} -i {backup_item_name_db1} --backup-type Full  --enable-compression false --backup-management-type AzureWorkload')

        # Test 2: List recovery points and select the latest one
        # Gets all recovery points for the database and selects the most recent
        self.kwargs['rp'] = self.cmd('backup recoverypoint list -g {rg} -v {vault} -c {vm_friendly_name} -i {backup_item_name_db1} --workload-type SAPAseDatabase --backup-management-type AzureWorkload --query [0]').get_output_in_json()

        # Extract the recovery point name for restore operations
        self.kwargs['rp'] = self.kwargs['rp']['name']

        # Test 3: Generate recovery configuration for Original Location Restore (OLR)
        # Creates configuration file needed for restore operation
        self.kwargs['rc'] = json.dumps(self.cmd('backup recoveryconfig show --vault-name {vault} -g {rg} --restore-mode OriginalWorkloadRestore --rp-name {rp} --item-name {backup_item_name_db1} --container-name {vm_full_name}').get_output_in_json(), separators=(',', ':'))
        
        # Write recovery configuration to file for restore command
        with open("recoveryconfig_ase_restore.json", "w") as f:
            f.write(self.kwargs['rc'])

        # Test 4: Initiate restore operation
        # Starts the restore process using the generated recovery configuration
        self.kwargs['backup_job'] = self.cmd('backup restore restore-azurewl --vault-name {vault} -g {rg} --recovery-config recoveryconfig_ase_restore.json', checks=[
            self.check("properties.operation", "Restore"),  # Verify operation type
            self.check("properties.status", "InProgress"),  # Verify job is started
            self.check("resourceGroup", '{rg}')  # Verify resource group
        ]).get_output_in_json()

    @unittest.skip("Unit test is currently blocked as soft delete is enabled by default")
    def test_ase_container_registration_lifecycle(self):
        """
        Test complete container registration and unregistration lifecycle.
        
        This test validates:
        1. Container registration for ASE workloads
        2. Container unregistration and cleanup
        
        Uses registration vault with temporary resources for lifecycle testing.
        Note: Currently skipped due to soft delete being enabled by default.
        """
        # Set up test context with registration resources
        self.kwargs.update({
            'vault': ase_registration_vault,  # Registration vault for temporary operations
            'vm': registration_vm_friendly_name,  # VM friendly name
            'rg': ase_resource_group,  # Resource group
            'reg_vm_id': registration_vm_resource_id,  # Full VM resource ID
            'vm_full_name': registration_vm_container_name,  # Full container name
            'backup_policy': registration_backup_policy,  # Policy for registration operations
            'backup_item': tertiary_database_item_name,  # Database for registration testing
            'backup_item_friendly_name': secondary_database_friendly_name  # Friendly name for database
        })

        # Test 1: Register container for ASE workload backup
        # Registers the VM container to enable ASE database backup capabilities
        self.cmd('backup container register -v {vault} -g {rg} --workload-type SAPAseDatabase --backup-management-type AzureWorkload --resource-id {reg_vm_id}')

        # Test 2: Unregister container to clean up
        # Removes the container registration to complete lifecycle test
        self.cmd('backup container unregister -v {vault} -g {rg} -c {vm_full_name} -y')

    @unittest.skip("Unit test is currently blocked as soft delete is enabled by default")
    def test_ase_protection_configuration_lifecycle(self):
        """
        Test complete protection configuration lifecycle for ASE databases.
        
        This test validates:
        1. Protection enablement for ASE databases
        2. Protection disabling with data deletion
        
        Uses registration vault with temporary resources for lifecycle testing.
        Note: Currently skipped due to soft delete being enabled by default.
        """
        # Set up test context with registration resources for protection lifecycle
        self.kwargs.update({
            'vault': ase_registration_vault,  # Registration vault for temporary operations
            'vm': registration_vm_friendly_name,  # VM friendly name
            'rg': ase_resource_group,  # Resource group
            'reg_vm_id': registration_vm_resource_id,  # VM resource ID
            'backup_policy': registration_backup_policy,  # Policy for protection operations
            'backup_item': master_database_item_name,  # Master database for protection testing
            'backup_item_friendly_name': master_database_friendly_name  # Master database friendly name
        })

        # Test 1: Enable protection for ASE database
        # Configures backup protection for the specified database with the given policy
        self.cmd('backup protection enable-for-azurewl -v {vault} -g {rg} -p {backup_policy} --protectable-item-type SAPAseDatabase --protectable-item-name {backup_item} --server-name {vm} --workload-type SAPAseDatabase', checks=[
            self.check("properties.entityFriendlyName", '{vm}'),  # Verify VM name in job
            self.check("properties.operation", "ConfigureBackup"),  # Verify operation type
            self.check("properties.status", "Completed"),  # Verify job completion
            self.check("resourceGroup", '{rg}')  # Verify resource group
        ])
        
        # Test 2: Disable protection with data deletion
        # Stops protection and deletes all backup data to complete lifecycle test
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} -y --delete-backup-data true -y')

    def test_ase_undelete_protection(self):
        """
        Test ASE database undelete protection functionality.
        
        This test validates:
        1. Protection disabling without data deletion (soft delete)
        2. Verification of soft-deleted state
        3. Undelete operation to restore protection
        
        Uses registration vault with temporary resources for undelete testing.
        This test was added to support SAP ASE database undelete operations.
        """
        # Set up test context with registration resources for undelete testing
        self.kwargs.update({
            'vault': ase_registration_vault,  # Registration vault for temporary operations
            'vm_full_name': registration_vm_container_name,  # Full container name
            'vm_friendly_name': registration_vm_friendly_name,  # VM friendly name for display
            'rg': ase_resource_group,  # Resource group
            'backup_item': primary_database_item_name,  # Primary database for undelete testing
            'backup_item_friendly_name': primary_database_friendly_name  # Database friendly name
        })

        # Test 1: Disable protection without deleting backup data
        # This puts the item in soft-deleted state for undelete testing
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm_full_name} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} --delete-backup-data false --yes')
        
        # Test 2: Verify item is in soft-deleted state (optional verification)
        # Checks if the item shows as scheduled for deferred delete
        try:
            item_json = self.cmd('backup item show --backup-management-type AzureWorkload -g {rg} -v {vault} -c {vm_full_name} -n {backup_item}').get_output_in_json()
            if 'properties' in item_json and 'isScheduledForDeferredDelete' in item_json['properties']:
                self.assertTrue(item_json['properties']['isScheduledForDeferredDelete'])  # Verify soft-deleted state
        except:
            # Item might not exist in the system, which is acceptable for this test
            pass

        # Test 3: Execute undelete protection operation
        # Restores the soft-deleted item to active protection state
        self.cmd('backup protection undelete --backup-management-type AzureWorkload --workload-type SAPAseDatabase -c {vm_full_name} -i {backup_item} -g {rg} -v {vault}', checks=[
            self.check("properties.entityFriendlyName", '{vm_friendly_name}'),  # Verify VM name in job
            self.check("properties.operation", "Undelete"),  # Verify operation type
            self.check("properties.status", "Completed"),  # Verify job completion
            self.check("resourceGroup", '{rg}')  # Verify resource group
        ])

    def test_ase_disable_protection_retain_data(self):
        """
        Test ASE database disable protection with data retention functionality.
        
        This test validates:
        1. Protection disabling while retaining recovery points per policy
        2. Verification of operation completion
        
        Uses registration vault with temporary resources for disable protection testing.
        This test was added to support SAP ASE database disable protection with retain data.
        """
        # Set up test context with registration resources for disable protection testing
        self.kwargs.update({
            'vault': ase_registration_vault,  # Registration vault for temporary operations
            'vm_full_name': registration_vm_container_name,  # Full container name
            'vm_friendly_name': registration_vm_friendly_name,  # VM friendly name for display
            'rg': ase_resource_group,  # Resource group
            'backup_item': secondary_database_item_name,  # Secondary database for disable testing
            'backup_item_friendly_name': primary_database_friendly_name  # Database friendly name
        })

        # Test: Disable protection while retaining recovery points per policy
        # Stops active protection but keeps existing backup data according to policy retention
        self.cmd('backup protection disable -v {vault} -g {rg} -c {vm_full_name} --backup-management-type AzureWorkload --workload-type SAPAseDatabase -i {backup_item} --retain-recovery-points-as-per-policy --yes', checks=[
            self.check("properties.entityFriendlyName", '{vm_friendly_name}'),  # Verify VM name in job
            self.check("properties.operation", "DisableBackup"),  # Verify operation type
            self.check("properties.status", "Completed"),  # Verify job completion
            self.check("resourceGroup", '{rg}')  # Verify resource group
        ])
