import 'package:flutter/material.dart';
import 'permission_card_base.dart';

class FieldPermissionsCard extends StatelessWidget {
  const FieldPermissionsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return PermissionCardBase(
      title: 'Field Permissions',
      subtitle: 'Field-level access control',
      icon: Icons.text_fields,
      color: const Color(0xfff59e0b),
      itemCount: 25,
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const FieldPermissionsDetailScreen(),
          ),
        );
      },
    );
  }
}

class FieldPermissionsDetailScreen extends StatefulWidget {
  const FieldPermissionsDetailScreen({super.key});

  @override
  State<FieldPermissionsDetailScreen> createState() => _FieldPermissionsDetailScreenState();
}

class _FieldPermissionsDetailScreenState extends State<FieldPermissionsDetailScreen> {
  String _selectedModule = 'user';
  
  final Map<String, List<FieldPermission>> _fieldsByModule = {
    'user': [
      FieldPermission('Email', 'email', FieldAccess.readWrite),
      FieldPermission('Password', 'password', FieldAccess.hidden),
      FieldPermission('Phone Number', 'phone', FieldAccess.readWrite),
      FieldPermission('Salary', 'salary', FieldAccess.hidden),
      FieldPermission('Address', 'address', FieldAccess.readOnly),
    ],
    'customer': [
      FieldPermission('Customer Name', 'name', FieldAccess.readWrite),
      FieldPermission('Credit Limit', 'credit_limit', FieldAccess.readOnly),
      FieldPermission('Payment Terms', 'payment_terms', FieldAccess.readWrite),
      FieldPermission('Internal Notes', 'notes', FieldAccess.hidden),
    ],
    'invoice': [
      FieldPermission('Invoice Number', 'number', FieldAccess.readOnly),
      FieldPermission('Amount', 'amount', FieldAccess.readOnly),
      FieldPermission('Tax', 'tax', FieldAccess.readWrite),
      FieldPermission('Discount', 'discount', FieldAccess.readWrite),
      FieldPermission('Cost Price', 'cost', FieldAccess.hidden),
    ],
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xfff59e0b),
        foregroundColor: Colors.white,
        title: const Text('Field Permissions', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: Column(
        children: [
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(value: 'user', label: Text('Users'), icon: Icon(Icons.person, size: 18)),
                      ButtonSegment(value: 'customer', label: Text('Customers'), icon: Icon(Icons.business, size: 18)),
                      ButtonSegment(value: 'invoice', label: Text('Invoices'), icon: Icon(Icons.receipt, size: 18)),
                    ],
                    selected: {_selectedModule},
                    onSelectionChanged: (Set<String> newSelection) {
                      setState(() => _selectedModule = newSelection.first);
                    },
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _fieldsByModule[_selectedModule]!.length,
              itemBuilder: (context, index) {
                final field = _fieldsByModule[_selectedModule]![index];
                return _buildFieldCard(field);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFieldCard(FieldPermission field) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(color: Colors.grey.withOpacity(0.1), blurRadius: 8, offset: const Offset(0, 2)),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: _getAccessColor(field.access).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(_getAccessIcon(field.access), color: _getAccessColor(field.access)),
        ),
        title: Text(field.name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(field.fieldName, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        trailing: PopupMenuButton<FieldAccess>(
          onSelected: (access) => setState(() => field.access = access),
          itemBuilder: (context) => [
            const PopupMenuItem(value: FieldAccess.readWrite, child: Row(children: [Icon(Icons.edit, size: 18), SizedBox(width: 8), Text('Read & Write')])),
            const PopupMenuItem(value: FieldAccess.readOnly, child: Row(children: [Icon(Icons.visibility, size: 18), SizedBox(width: 8), Text('Read Only')])),
            const PopupMenuItem(value: FieldAccess.hidden, child: Row(children: [Icon(Icons.visibility_off, size: 18), SizedBox(width: 8), Text('Hidden')])),
          ],
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _getAccessColor(field.access).withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(_getAccessIcon(field.access), size: 16, color: _getAccessColor(field.access)),
                const SizedBox(width: 6),
                Text(_getAccessText(field.access), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: _getAccessColor(field.access))),
                const SizedBox(width: 4),
                Icon(Icons.arrow_drop_down, size: 18, color: _getAccessColor(field.access)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  IconData _getAccessIcon(FieldAccess access) {
    switch (access) {
      case FieldAccess.readWrite: return Icons.edit;
      case FieldAccess.readOnly: return Icons.visibility;
      case FieldAccess.hidden: return Icons.visibility_off;
    }
  }

  Color _getAccessColor(FieldAccess access) {
    switch (access) {
      case FieldAccess.readWrite: return const Color(0xff10b981);
      case FieldAccess.readOnly: return const Color(0xff3b82f6);
      case FieldAccess.hidden: return const Color(0xff6b7280);
    }
  }

  String _getAccessText(FieldAccess access) {
    switch (access) {
      case FieldAccess.readWrite: return 'Read & Write';
      case FieldAccess.readOnly: return 'Read Only';
      case FieldAccess.hidden: return 'Hidden';
    }
  }
}

enum FieldAccess { readWrite, readOnly, hidden }

class FieldPermission {
  final String name;
  final String fieldName;
  FieldAccess access;
  FieldPermission(this.name, this.fieldName, this.access);
}
