import 'package:flutter/material.dart';
import 'widgets/module_permissions_card.dart';
import 'widgets/data_scope_permissions_card.dart';
import 'widgets/application_access_card.dart';
import 'widgets/permission_groups_card.dart';
import 'widgets/field_permissions_card.dart';
import 'widgets/action_permissions_card.dart';

/// Permissions Tab - Display comprehensive permission management cards
///
/// This tab provides granular control over:
/// - Module Permissions (which modules users can access)
/// - Data Scope Permissions (what data they can see/edit)
/// - Application Access (which apps they can use)
/// - Permission Groups (predefined permission sets)
/// - Field Permissions (field-level access control)
/// - Action Permissions (CRUD operations)
class PermissionsTab extends StatefulWidget {
  const PermissionsTab({super.key});

  @override
  State<PermissionsTab> createState() => _PermissionsTabState();
}

class _PermissionsTabState extends State<PermissionsTab> {
  @override
  void initState() {
    super.initState();
    print('🔐 Permissions Tab: Initialized');
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async {
        print('🔄 Refreshing permissions...');
        // Refresh all permission cards
        setState(() {});
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            _buildHeader(),
            const SizedBox(height: 24),

            // Permission Cards Grid
            _buildPermissionCards(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xff7c3aed), Color(0xff5b21b6)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xff7c3aed).withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.security,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Permission Management',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Granular access control system',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPermissionCards() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section Title
        Text(
          'Permission Categories',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.grey[800],
          ),
        ),
        const SizedBox(height: 16),

        // 1. Module Permissions Card
        const ModulePermissionsCard(),
        const SizedBox(height: 16),

        // 2. Data Scope Permissions Card
        const DataScopePermissionsCard(),
        const SizedBox(height: 16),

        // 3. Application Access Card
        const ApplicationAccessCard(),
        const SizedBox(height: 16),

        // 4. Permission Groups Card
        const PermissionGroupsCard(),
        const SizedBox(height: 16),

        // 5. Field Permissions Card
        const FieldPermissionsCard(),
        const SizedBox(height: 16),

        // 6. Action Permissions Card
        const ActionPermissionsCard(),
        const SizedBox(height: 24),

        // Help Card
        _buildHelpCard(),
      ],
    );
  }

  Widget _buildHelpCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xff3b82f6).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xff3b82f6).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.info_outline,
            color: Color(0xff3b82f6),
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Multi-Level Permission System',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Color(0xff3b82f6),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Click on any card to configure detailed permissions for each category.',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
