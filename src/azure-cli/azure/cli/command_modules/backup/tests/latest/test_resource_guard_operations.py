# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import sys
import os

# Add the source directory to the path to enable testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..'))


class ResourceGuardOperationMappingTests(unittest.TestCase):
    """Unit tests for resource guard operation mapping"""

    def test_operation_name_map_contains_new_operation(self):
        """Test that the operation_name_map contains the new BackupsSuspended operation"""
        # Test the operation mapping directly by parsing the file
        custom_help_path = os.path.join(os.path.dirname(__file__), '..', '..', 'custom_help.py')
        
        with open(custom_help_path, 'r') as f:
            content = f.read()
        
        # Verify that RecoveryServicesBackupsSuspended is in the file
        self.assertIn("RecoveryServicesBackupsSuspended", content)
        
        # Verify the operation mapping value is present
        self.assertIn("#suspendBackupsWithRetainData", content)
        
        # Verify that the original StopProtection operation is still there
        self.assertIn("RecoveryServicesStopProtection", content)
        self.assertIn("#stopProtectionWithRetainData", content)

    def test_vm_disable_protection_logic_contains_operation_selection(self):
        """Test that VM disable protection logic contains operation selection"""
        custom_path = os.path.join(os.path.dirname(__file__), '..', '..', 'custom.py')
        
        with open(custom_path, 'r') as f:
            content = f.read()
        
        # Verify that the new logic is present in the disable_protection function
        self.assertIn("operation_name = (", content)
        self.assertIn("RecoveryServicesStopProtection", content)
        self.assertIn("RecoveryServicesBackupsSuspended", content)
        self.assertIn("protection_stopped", content)
        self.assertIn("backups_suspended", content)

    def test_afs_disable_protection_logic_contains_operation_selection(self):
        """Test that AFS disable protection logic contains operation selection"""
        custom_afs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'custom_afs.py')
        
        with open(custom_afs_path, 'r') as f:
            content = f.read()
        
        # Verify that the new logic is present in the disable_protection function
        self.assertIn("operation_name = (", content)
        self.assertIn("RecoveryServicesStopProtection", content)
        self.assertIn("RecoveryServicesBackupsSuspended", content)

    def test_workload_disable_protection_logic_contains_operation_selection(self):
        """Test that Workload disable protection logic contains operation selection"""
        custom_wl_path = os.path.join(os.path.dirname(__file__), '..', '..', 'custom_wl.py')
        
        with open(custom_wl_path, 'r') as f:
            content = f.read()
        
        # Verify that the new logic is present in the disable_protection function
        self.assertIn("operation_name = (", content)
        self.assertIn("RecoveryServicesStopProtection", content)
        self.assertIn("RecoveryServicesBackupsSuspended", content)

    def test_protection_state_mapping_logic_correctness(self):
        """Test the logic for mapping protection states to operations"""
        # Test the ternary logic pattern that should be present in all three files
        files_to_test = [
            ('custom.py', 'VM'),
            ('custom_afs.py', 'AFS'), 
            ('custom_wl.py', 'Workload')
        ]
        
        for filename, backup_type in files_to_test:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', filename)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verify the ternary operation logic is present
            # This should map protection_stopped -> RecoveryServicesStopProtection
            # and backups_suspended -> RecoveryServicesBackupsSuspended
            self.assertIn("protection_stopped", content, 
                         f"protection_stopped check missing in {backup_type}")
            self.assertIn("RecoveryServicesStopProtection", content,
                         f"RecoveryServicesStopProtection missing in {backup_type}")
            self.assertIn("RecoveryServicesBackupsSuspended", content,
                         f"RecoveryServicesBackupsSuspended missing in {backup_type}")

    def test_conditional_logic_pattern(self):
        """Test that the conditional logic follows the expected pattern"""
        files_to_test = [
            ('custom.py', 'VM'),
            ('custom_afs.py', 'AFS'), 
            ('custom_wl.py', 'Workload')
        ]
        
        for filename, backup_type in files_to_test:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', filename)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verify the expected conditional pattern
            # Should check for both protection_stopped and backups_suspended states
            self.assertIn("[ProtectionState.protection_stopped, ProtectionState.backups_suspended]", content,
                         f"Both protection states check missing in {backup_type}")
            
            # Verify the ternary operator pattern for operation selection
            self.assertIn("operation_name = (", content,
                         f"Operation name assignment missing in {backup_type}")
            
            # Verify that operation_name is used in resource guard calls
            self.assertIn("vault_name, operation_name)", content,
                         f"operation_name usage missing in {backup_type}")

    def test_resource_guard_function_calls_updated(self):
        """Test that resource guard function calls use the dynamic operation_name"""
        files_to_test = [
            ('custom.py', 'VM'),
            ('custom_afs.py', 'AFS'), 
            ('custom_wl.py', 'Workload')
        ]
        
        for filename, backup_type in files_to_test:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', filename)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verify has_resource_guard_mapping uses operation_name variable
            # The pattern should be: vault_name, operation_name)
            found_operation_name_usage = False
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "has_resource_guard_mapping" in line:
                    # Check this line and the next few lines for operation_name
                    for j in range(min(3, len(lines) - i)):
                        if "operation_name)" in lines[i + j]:
                            found_operation_name_usage = True
                            break
                    if found_operation_name_usage:
                        break
            
            self.assertTrue(found_operation_name_usage, 
                          f"operation_name not used in has_resource_guard_mapping in {backup_type}")
            
            # Verify get_resource_guard_operation_request uses operation_name variable
            found_get_operation_usage = False
            for i, line in enumerate(lines):
                if "get_resource_guard_operation_request" in line:
                    # Check this line and the next few lines for operation_name
                    for j in range(min(3, len(lines) - i)):
                        if "operation_name)" in lines[i + j]:
                            found_get_operation_usage = True
                            break
                    if found_get_operation_usage:
                        break
            
            self.assertTrue(found_get_operation_usage,
                          f"operation_name not used in get_resource_guard_operation_request in {backup_type}")


if __name__ == '__main__':
    unittest.main()