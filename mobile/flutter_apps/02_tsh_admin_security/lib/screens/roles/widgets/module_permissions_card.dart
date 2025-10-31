import 'package:flutter/material.dart';

/// Module Permissions Card
/// Controls which system modules users can access
/// Examples: HR, Inventory, Sales, Accounting, etc.
class ModulePermissionsCard extends StatelessWidget {
  const ModulePermissionsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return _buildPermissionCard(
      context: context,
      title: 'Module Permissions',
      subtitle: 'Control access to system modules',
      icon: Icons.apps,
      color: const Color(0xff7c3aed),
      itemCount: 12,
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ModulePermissionsDetailScreen(),
          ),
        );
      },
    );
  }

  Widget _buildPermissionCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required int itemCount,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(icon, color: color, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xff1f2937),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '$itemCount modules',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: color,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 18,
                  color: Colors.grey[400],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Module Permissions Detail Screen
class ModulePermissionsDetailScreen extends StatefulWidget {
  const ModulePermissionsDetailScreen({super.key});

  @override
  State<ModulePermissionsDetailScreen> createState() =>
      _ModulePermissionsDetailScreenState();
}

class _ModulePermissionsDetailScreenState
    extends State<ModulePermissionsDetailScreen> {
  final List<ModulePermission> _modules = [
    ModulePermission('Dashboard', Icons.dashboard, true),
    ModulePermission('User Management', Icons.people, true),
    ModulePermission('HR Management', Icons.badge, false),
    ModulePermission('Inventory', Icons.inventory, true),
    ModulePermission('Sales & CRM', Icons.point_of_sale, true),
    ModulePermission('Purchases', Icons.shopping_cart, false),
    ModulePermission('Accounting', Icons.account_balance, false),
    ModulePermission('POS', Icons.receipt_long, true),
    ModulePermission('Cashflow', Icons.attach_money, false),
    ModulePermission('Reports', Icons.analytics, true),
    ModulePermission('Settings', Icons.settings, false),
    ModulePermission('Security', Icons.security, true),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff7c3aed),
        foregroundColor: Colors.white,
        title: const Text(
          'Module Permissions',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          TextButton.icon(
            onPressed: () {
              setState(() {
                final allEnabled = _modules.every((m) => m.isEnabled);
                for (var module in _modules) {
                  module.isEnabled = !allEnabled;
                }
              });
            },
            icon: const Icon(Icons.select_all, color: Colors.white),
            label: const Text(
              'Toggle All',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _modules.length,
        itemBuilder: (context, index) {
          final module = _modules[index];
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: SwitchListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 8,
              ),
              secondary: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: module.isEnabled
                      ? const Color(0xff7c3aed).withOpacity(0.1)
                      : Colors.grey.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  module.icon,
                  color: module.isEnabled
                      ? const Color(0xff7c3aed)
                      : Colors.grey,
                  size: 24,
                ),
              ),
              title: Text(
                module.name,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
              subtitle: Text(
                module.isEnabled ? 'Access granted' : 'Access denied',
                style: TextStyle(
                  fontSize: 13,
                  color: module.isEnabled
                      ? const Color(0xff10b981)
                      : Colors.grey,
                ),
              ),
              value: module.isEnabled,
              activeColor: const Color(0xff7c3aed),
              onChanged: (value) {
                setState(() {
                  module.isEnabled = value;
                });
              },
            ),
          );
        },
      ),
    );
  }
}

class ModulePermission {
  final String name;
  final IconData icon;
  bool isEnabled;

  ModulePermission(this.name, this.icon, this.isEnabled);
}
