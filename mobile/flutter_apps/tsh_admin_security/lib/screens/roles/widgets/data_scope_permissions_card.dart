import 'package:flutter/material.dart';
import 'permission_card_base.dart';

/// Data Scope Permissions Card
/// Controls what data users can see and modify
/// Examples: Own data, Branch data, Company-wide data
class DataScopePermissionsCard extends StatelessWidget {
  const DataScopePermissionsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return PermissionCardBase(
      title: 'Data Scope Permissions',
      subtitle: 'Control data visibility and access scope',
      icon: Icons.data_usage,
      color: const Color(0xff3b82f6),
      itemCount: 5,
      onTap: () {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (context) => _DataScopeSheet(),
        );
      },
    );
  }
}

class _DataScopeSheet extends StatefulWidget {
  @override
  State<_DataScopeSheet> createState() => _DataScopeSheetState();
}

class _DataScopeSheetState extends State<_DataScopeSheet> {
  String _selectedScope = 'branch';

  final List<Map<String, dynamic>> _scopes = [
    {
      'id': 'own',
      'title': 'Own Data Only',
      'subtitle': 'Can only view/edit their own records',
      'icon': Icons.person,
    },
    {
      'id': 'branch',
      'title': 'Branch Level',
      'subtitle': 'Access to all data within their branch',
      'icon': Icons.store,
    },
    {
      'id': 'region',
      'title': 'Regional Level',
      'subtitle': 'Access across multiple branches in region',
      'icon': Icons.map,
    },
    {
      'id': 'company',
      'title': 'Company Wide',
      'subtitle': 'Access to all company data',
      'icon': Icons.business,
    },
    {
      'id': 'custom',
      'title': 'Custom Scope',
      'subtitle': 'Define custom data access rules',
      'icon': Icons.tune,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xff3b82f6),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
            ),
            child: Row(
              children: [
                const Icon(Icons.data_usage, color: Colors.white, size: 28),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Data Scope Permissions',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _scopes.length,
              itemBuilder: (context, index) {
                final scope = _scopes[index];
                final isSelected = _selectedScope == scope['id'];
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xff3b82f6).withOpacity(0.1)
                        : Colors.grey[50],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xff3b82f6)
                          : Colors.grey[300]!,
                      width: 2,
                    ),
                  ),
                  child: RadioListTile<String>(
                    value: scope['id'],
                    groupValue: _selectedScope,
                    onChanged: (value) {
                      setState(() => _selectedScope = value!);
                    },
                    title: Text(
                      scope['title'],
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: isSelected
                            ? const Color(0xff3b82f6)
                            : Colors.black87,
                      ),
                    ),
                    subtitle: Text(scope['subtitle']),
                    secondary: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? const Color(0xff3b82f6)
                            : Colors.grey[300],
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        scope['icon'],
                        color: isSelected ? Colors.white : Colors.grey[600],
                      ),
                    ),
                    activeColor: const Color(0xff3b82f6),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
