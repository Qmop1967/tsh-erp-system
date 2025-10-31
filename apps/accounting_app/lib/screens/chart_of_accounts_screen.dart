import 'package:flutter/material.dart';
import '../config/app_config.dart';

/// Chart of Accounts Screen
/// شاشة دليل الحسابات

class ChartOfAccountsScreen extends StatelessWidget {
  const ChartOfAccountsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('دليل الحسابات'),
        backgroundColor: Color(AppConfig.primaryColorValue),
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('قريباً: دليل الحسابات'),
      ),
    );
  }
}
