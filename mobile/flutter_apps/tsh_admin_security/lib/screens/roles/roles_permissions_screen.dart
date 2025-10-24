import 'package:flutter/material.dart';
import 'roles_tab.dart';
import 'permissions_tab.dart';

/// Professional Roles & Permissions Management Screen
/// Features:
/// - Two-tab interface (Roles | Permissions)
/// - Multi-level permission control system
/// - Granular access management
class RolesPermissionsScreen extends StatefulWidget {
  const RolesPermissionsScreen({super.key});

  @override
  State<RolesPermissionsScreen> createState() => _RolesPermissionsScreenState();
}

class _RolesPermissionsScreenState extends State<RolesPermissionsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    print('📋 Roles & Permissions Screen: Initialized');
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff7c3aed),
        foregroundColor: Colors.white,
        title: const Text(
          'Roles & Permissions',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          indicatorWeight: 3,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          labelStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          tabs: const [
            Tab(
              icon: Icon(Icons.badge_outlined),
              text: 'Roles',
            ),
            Tab(
              icon: Icon(Icons.security),
              text: 'Permissions',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          RolesTab(),
          PermissionsTab(),
        ],
      ),
    );
  }
}
