import 'package:flutter/material.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

class BarcodeScanningScreen extends StatefulWidget {
  const BarcodeScanningScreen({super.key});

  @override
  State<BarcodeScanningScreen> createState() => _BarcodeScanningScreenState();
}

class _BarcodeScanningScreenState extends State<BarcodeScanningScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Barcode Scanner'),
        subtitle: const Text('Phase 5 Feature - Coming Soon'),
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.qr_code_scanner,
              size: 64,
              color: TSHTheme.primaryTeal,
            ),
            SizedBox(height: 16),
            Text(
              'Barcode Scanning',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Phase 5: Mobile & Integration',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            SizedBox(height: 16),
            Text(
              'Coming Soon:',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 8),
            Text('• Barcode scanning functionality'),
            Text('• QR code support'),
            Text('• Label printing system'),
            Text('• Mobile stock movements'),
            Text('• Offline capability'),
          ],
        ),
      ),
    );
  }
}

class InventorySettingsScreen extends StatefulWidget {
  const InventorySettingsScreen({super.key});

  @override
  State<InventorySettingsScreen> createState() => _InventorySettingsScreenState();
}

class _InventorySettingsScreenState extends State<InventorySettingsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.sync),
              title: const Text('Sync Settings'),
              subtitle: const Text('Configure data synchronization'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {},
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.notifications),
              title: const Text('Alert Settings'),
              subtitle: const Text('Low stock and notification preferences'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {},
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.security),
              title: const Text('Security'),
              subtitle: const Text('User permissions and access control'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {},
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.backup),
              title: const Text('Backup & Export'),
              subtitle: const Text('Data backup and export options'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {},
            ),
          ),
        ],
      ),
    );
  }
}
