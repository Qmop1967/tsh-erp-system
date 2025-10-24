import 'package:flutter/material.dart';
import 'permission_card_base.dart';

class ActionPermissionsCard extends StatelessWidget {
  const ActionPermissionsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return PermissionCardBase(
      title: 'Action Permissions',
      subtitle: 'CRUD operations control',
      icon: Icons.touch_app,
      color: const Color(0xff8b5cf6),
      itemCount: 4,
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ActionPermissionsDetailScreen(),
          ),
        );
      },
    );
  }
}

class ActionPermissionsDetailScreen extends StatefulWidget {
  const ActionPermissionsDetailScreen({super.key});

  @override
  State<ActionPermissionsDetailScreen> createState() => _ActionPermissionsDetailScreenState();
}

class _ActionPermissionsDetailScreenState extends State<ActionPermissionsDetailScreen> {
  final List<ModuleActions> _modules = [
    ModuleActions('Users', Icons.people, {
      'create': true,
      'read': true,
      'update': true,
      'delete': false,
    }),
    ModuleActions('Customers', Icons.business, {
      'create': true,
      'read': true,
      'update': true,
      'delete': true,
    }),
    ModuleActions('Products', Icons.inventory_2, {
      'create': false,
      'read': true,
      'update': false,
      'delete': false,
    }),
    ModuleActions('Invoices', Icons.receipt, {
      'create': true,
      'read': true,
      'update': true,
      'delete': false,
    }),
    ModuleActions('Reports', Icons.analytics, {
      'create': false,
      'read': true,
      'update': false,
      'delete': false,
    }),
    ModuleActions('Settings', Icons.settings, {
      'create': false,
      'read': true,
      'update': true,
      'delete': false,
    }),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff8b5cf6),
        foregroundColor: Colors.white,
        title: const Text('Action Permissions', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _modules.length,
        itemBuilder: (context, index) {
          final module = _modules[index];
          return _buildModuleCard(module);
        },
      ),
    );
  }

  Widget _buildModuleCard(ModuleActions module) {
    final activeCount = module.actions.values.where((v) => v).length;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: Colors.grey.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, 2)),
        ],
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(20),
        childrenPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
        leading: Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xff8b5cf6), Color(0xff7c3aed)],
            ),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(module.icon, color: Colors.white, size: 28),
        ),
        title: Text(module.name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
        subtitle: Container(
          margin: const EdgeInsets.only(top: 8),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: const Color(0xff8b5cf6).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '$activeCount of 4 actions enabled',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xff8b5cf6)),
          ),
        ),
        children: [
          const Divider(),
          const SizedBox(height: 12),
          _buildActionRow('Create', 'create', Icons.add_circle, const Color(0xff10b981), module),
          const SizedBox(height: 12),
          _buildActionRow('Read', 'read', Icons.visibility, const Color(0xff3b82f6), module),
          const SizedBox(height: 12),
          _buildActionRow('Update', 'update', Icons.edit, const Color(0xfff59e0b), module),
          const SizedBox(height: 12),
          _buildActionRow('Delete', 'delete', Icons.delete, const Color(0xffef4444), module),
        ],
      ),
    );
  }

  Widget _buildActionRow(String label, String key, IconData icon, Color color, ModuleActions module) {
    final isEnabled = module.actions[key]!;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isEnabled ? color.withOpacity(0.05) : Colors.grey.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isEnabled ? color.withOpacity(0.3) : Colors.grey.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: isEnabled ? color : Colors.grey,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isEnabled ? color : Colors.grey[700],
                  ),
                ),
                Text(
                  isEnabled ? 'Enabled' : 'Disabled',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          Switch(
            value: isEnabled,
            activeColor: color,
            onChanged: (value) {
              setState(() {
                module.actions[key] = value;
              });
            },
          ),
        ],
      ),
    );
  }
}

class ModuleActions {
  final String name;
  final IconData icon;
  final Map<String, bool> actions;
  ModuleActions(this.name, this.icon, this.actions);
}
