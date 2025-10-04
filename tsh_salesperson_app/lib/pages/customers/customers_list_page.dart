import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';

import '../../config/app_theme.dart';

class CustomersListPage extends StatelessWidget {
  const CustomersListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      appBar: AppBar(
        title: const Text('العملاء'),
        backgroundColor: AppTheme.primaryGreen,
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              MdiIcons.accountGroup,
              size: 100,
              color: AppTheme.textLight.withOpacity(0.5),
            ),
            const SizedBox(height: 20),
            const Text(
              'صفحة العملاء',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.textDark,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'قيد التطوير',
              style: TextStyle(
                fontSize: 16,
                color: AppTheme.textLight,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
