import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';

import '../../config/app_theme.dart';
import '../dashboard/dashboard_container_page.dart';
import '../customers/customers_list_page.dart';
import '../sales/pos_page.dart';
import '../orders/orders_list_page.dart';
import '../menu/menu_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const DashboardContainerPage(),
    const CustomersListPage(),
    const POSPage(),
    const OrdersListPage(),
    const MenuPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: _buildBottomNavigationBar(),
    );
  }

  Widget _buildBottomNavigationBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(25),
          topRight: Radius.circular(25),
        ),
      ),
      child: ClipRRect(
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(25),
          topRight: Radius.circular(25),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: AppTheme.primaryGreen,
          unselectedItemColor: AppTheme.textLight,
          selectedFontSize: 12,
          unselectedFontSize: 11,
          elevation: 0,
          items: [
            BottomNavigationBarItem(
              icon: _buildNavIcon(MdiIcons.viewDashboard, 0),
              label: 'الرئيسية',
            ),
            BottomNavigationBarItem(
              icon: _buildNavIcon(MdiIcons.accountGroup, 1),
              label: 'العملاء',
            ),
            BottomNavigationBarItem(
              icon: _buildNavIcon(MdiIcons.cashRegister, 2),
              label: 'نقطة البيع',
            ),
            BottomNavigationBarItem(
              icon: _buildNavIcon(MdiIcons.clipboardText, 3),
              label: 'الطلبات',
            ),
            BottomNavigationBarItem(
              icon: _buildNavIcon(MdiIcons.menu, 4),
              label: 'القائمة',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavIcon(IconData icon, int index) {
    final isSelected = _currentIndex == index;
    
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: isSelected
            ? AppTheme.primaryGreen.withOpacity(0.1)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(
        icon,
        size: 26,
      ),
    );
  }
}
