import 'package:flutter/material.dart';
import 'permission_card_base.dart';

/// Application Access Card - Full Implementation
/// Controls which mobile applications users can access
class ApplicationAccessCard extends StatelessWidget {
  const ApplicationAccessCard({super.key});

  @override
  Widget build(BuildContext context) {
    return PermissionCardBase(
      title: 'Application Access',
      subtitle: 'Control which apps users can access',
      icon: Icons.phone_android,
      color: const Color(0xff10b981),
      itemCount: 8,
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ApplicationAccessDetailScreen(),
          ),
        );
      },
    );
  }
}

class ApplicationAccessDetailScreen extends StatefulWidget {
  const ApplicationAccessDetailScreen({super.key});

  @override
  State<ApplicationAccessDetailScreen> createState() =>
      _ApplicationAccessDetailScreenState();
}

class _ApplicationAccessDetailScreenState
    extends State<ApplicationAccessDetailScreen> {
  final List<AppAccess> _apps = [
    AppAccess(
      'TSH Admin Dashboard',
      'Full admin control panel',
      Icons.dashboard,
      const Color(0xff7c3aed),
      true,
      ['Admin', 'Manager'],
    ),
    AppAccess(
      'TSH HR Management',
      'Employee & payroll management',
      Icons.badge,
      const Color(0xff3b82f6),
      false,
      ['HR', 'Manager'],
    ),
    AppAccess(
      'TSH Salesperson App',
      'Sales on the go',
      Icons.shopping_bag,
      const Color(0xff10b981),
      true,
      ['Salesperson', 'Manager'],
    ),
    AppAccess(
      'TSH Inventory App',
      'Stock & warehouse management',
      Icons.inventory_2,
      const Color(0xfff59e0b),
      true,
      ['Inventory', 'Manager'],
    ),
    AppAccess(
      'TSH Retail Sales',
      'POS & retail operations',
      Icons.point_of_sale,
      const Color(0xffef4444),
      false,
      ['Cashier', 'Manager'],
    ),
    AppAccess(
      'TSH Partner Network',
      'B2B partner portal',
      Icons.handshake,
      const Color(0xff8b5cf6),
      false,
      ['Partner'],
    ),
    AppAccess(
      'TSH Wholesale Client',
      'Wholesale customer app',
      Icons.business,
      const Color(0xff06b6d4),
      true,
      ['Wholesale Client'],
    ),
    AppAccess(
      'TSH Consumer App',
      'B2C retail shopping',
      Icons.shopping_cart,
      const Color(0xffec4899),
      false,
      ['Consumer'],
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final enabledCount = _apps.where((app) => app.isEnabled).length;

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff10b981),
        foregroundColor: Colors.white,
        title: const Text(
          'Application Access',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Container(
            padding: const EdgeInsets.all(16),
            color: const Color(0xff10b981),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '$enabledCount of ${_apps.length} apps enabled',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                TextButton.icon(
                  onPressed: () {
                    setState(() {
                      final allEnabled = _apps.every((a) => a.isEnabled);
                      for (var app in _apps) {
                        app.isEnabled = !allEnabled;
                      }
                    });
                  },
                  icon: const Icon(Icons.select_all, color: Colors.white, size: 20),
                  label: const Text(
                    'Toggle All',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _apps.length,
        itemBuilder: (context, index) {
          final app = _apps[index];
          return _buildAppCard(app);
        },
      ),
    );
  }

  Widget _buildAppCard(AppAccess app) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: app.isEnabled
              ? app.color.withOpacity(0.3)
              : Colors.grey.withOpacity(0.2),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: app.isEnabled
                ? app.color.withOpacity(0.1)
                : Colors.grey.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          SwitchListTile(
            contentPadding: const EdgeInsets.all(20),
            secondary: Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                gradient: app.isEnabled
                    ? LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [app.color, app.color.withOpacity(0.7)],
                      )
                    : null,
                color: app.isEnabled ? null : Colors.grey[300],
                borderRadius: BorderRadius.circular(14),
                boxShadow: app.isEnabled
                    ? [
                        BoxShadow(
                          color: app.color.withOpacity(0.3),
                          blurRadius: 8,
                          offset: const Offset(0, 4),
                        ),
                      ]
                    : null,
              ),
              child: Icon(
                app.icon,
                color: app.isEnabled ? Colors.white : Colors.grey[600],
                size: 28,
              ),
            ),
            title: Text(
              app.name,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: app.isEnabled ? app.color : Colors.grey[700],
              ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(
                  app.description,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: app.recommendedFor.map((role) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: app.isEnabled
                            ? app.color.withOpacity(0.1)
                            : Colors.grey[200],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        role,
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: app.isEnabled ? app.color : Colors.grey[600],
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
            value: app.isEnabled,
            activeColor: app.color,
            onChanged: (value) {
              setState(() {
                app.isEnabled = value;
              });
            },
          ),
        ],
      ),
    );
  }
}

class AppAccess {
  final String name;
  final String description;
  final IconData icon;
  final Color color;
  bool isEnabled;
  final List<String> recommendedFor;

  AppAccess(
    this.name,
    this.description,
    this.icon,
    this.color,
    this.isEnabled,
    this.recommendedFor,
  );
}
