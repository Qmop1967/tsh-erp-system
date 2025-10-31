import 'package:flutter/material.dart';
import '../config/app_config.dart';

/// Journal Entries Screen
/// شاشة القيود اليومية

class JournalEntriesScreen extends StatelessWidget {
  const JournalEntriesScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('القيود اليومية'),
        backgroundColor: Color(AppConfig.primaryColorValue),
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text('قريباً: القيود اليومية'),
      ),
    );
  }
}
