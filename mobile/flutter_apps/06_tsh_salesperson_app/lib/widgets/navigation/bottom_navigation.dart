import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:animated_bottom_navigation_bar/animated_bottom_navigation_bar.dart';

import '../../config/app_theme.dart';

class TSHBottomNavigation extends StatefulWidget {
  final int currentIndex;
  final Function(int) onTap;
  final VoidCallback? onFABPressed;

  const TSHBottomNavigation({
    super.key,
    required this.currentIndex,
    required this.onTap,
    this.onFABPressed,
  });

  @override
  State<TSHBottomNavigation> createState() => _TSHBottomNavigationState();
}

class _TSHBottomNavigationState extends State<TSHBottomNavigation>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;
  late AnimationController _fabAnimationController;
  late Animation<double> _fabAnimation;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _animation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    
    _fabAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _fabAnimation = CurvedAnimation(
      parent: _fabAnimationController,
      curve: Curves.elasticOut,
    );
    
    _animationController.forward();
    _fabAnimationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _fabAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: AnimatedBottomNavigationBar.builder(
        itemCount: _navItems.length,
        tabBuilder: (int index, bool isActive) {
          final item = _navItems[index];
          final color = isActive ? AppTheme.primaryGreen : AppTheme.textLight;
          
          return Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: EdgeInsets.all(isActive ? 8 : 4),
                decoration: BoxDecoration(
                  color: isActive 
                    ? AppTheme.primaryGreen.withOpacity(0.1)
                    : Colors.transparent,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  item.icon,
                  size: isActive ? 26 : 22,
                  color: color,
                ),
              ),
              const SizedBox(height: 4),
              AnimatedDefaultTextStyle(
                duration: const Duration(milliseconds: 200),
                style: TextStyle(
                  color: color,
                  fontSize: isActive ? 12 : 11,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
                  fontFamily: 'Cairo',
                ),
                child: Text(item.label),
              ),
            ],
          );
        },
        backgroundColor: Colors.white,
        activeIndex: widget.currentIndex,
        onTap: widget.onTap,
        gapLocation: GapLocation.center,
        notchSmoothness: NotchSmoothness.softEdge,
        leftCornerRadius: 20,
        rightCornerRadius: 20,
        height: 75,
        splashRadius: 0,
        elevation: 0,
      ),
    );
  }

  static final List<BottomNavItem> _navItems = [
    BottomNavItem(
      icon: MdiIcons.viewDashboard,
      label: 'لوحة التحكم',
    ),
    BottomNavItem(
      icon: MdiIcons.accountGroup,
      label: 'العملاء',
    ),
    BottomNavItem(
      icon: MdiIcons.packageVariant,
      label: 'المنتجات',
    ),
    BottomNavItem(
      icon: MdiIcons.receiptText,
      label: 'الطلبات',
    ),
  ];
}

class BottomNavItem {
  final IconData icon;
  final String label;

  const BottomNavItem({
    required this.icon,
    required this.label,
  });
}

class TSHFloatingActionButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final String tooltip;

  const TSHFloatingActionButton({
    super.key,
    this.onPressed,
    this.icon = Icons.add,
    this.tooltip = 'إضافة',
  });

  @override
  State<TSHFloatingActionButton> createState() => _TSHFloatingActionButtonState();
}

class _TSHFloatingActionButtonState extends State<TSHFloatingActionButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
    
    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 0.1,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    _controller.forward();
  }

  void _onTapUp(TapUpDetails details) {
    _controller.reverse();
  }

  void _onTapCancel() {
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Transform.rotate(
            angle: _rotationAnimation.value,
            child: GestureDetector(
              onTapDown: _onTapDown,
              onTapUp: _onTapUp,
              onTapCancel: _onTapCancel,
              onTap: widget.onPressed,
              child: Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  gradient: AppTheme.goldGradient,
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.goldAccent.withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Icon(
                  widget.icon,
                  color: Colors.white,
                  size: 28,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class HiddenSideMenu extends StatefulWidget {
  final bool isVisible;
  final VoidCallback onClose;
  final Function(String) onMenuItemTap;

  const HiddenSideMenu({
    super.key,
    required this.isVisible,
    required this.onClose,
    required this.onMenuItemTap,
  });

  @override
  State<HiddenSideMenu> createState() => _HiddenSideMenuState();
}

class _HiddenSideMenuState extends State<HiddenSideMenu>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(-1.0, 0.0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 0.5,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(HiddenSideMenu oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isVisible) {
      _controller.forward();
    } else {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Backdrop
        AnimatedBuilder(
          animation: _fadeAnimation,
          builder: (context, child) {
            return GestureDetector(
              onTap: widget.onClose,
              child: Container(
                color: Colors.black.withOpacity(_fadeAnimation.value),
              ),
            );
          },
        ),
        
        // Side Menu
        SlideTransition(
          position: _slideAnimation,
          child: Container(
            width: MediaQuery.of(context).size.width * 0.85,
            height: double.infinity,
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.horizontal(
                right: Radius.circular(24),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black12,
                  blurRadius: 20,
                  offset: Offset(5, 0),
                ),
              ],
            ),
            child: Column(
              children: [
                // Header
                Container(
                  height: 120,
                  decoration: const BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.only(
                      topRight: Radius.circular(24),
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        children: [
                          CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.white.withOpacity(0.2),
                            child: const Icon(
                              MdiIcons.account,
                              color: Colors.white,
                              size: 28,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Text(
                                  'مندوب المبيعات',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    fontFamily: 'Cairo',
                                  ),
                                ),
                                Text(
                                  'TSH Company',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.8),
                                    fontSize: 12,
                                    fontFamily: 'Cairo',
                                  ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            onPressed: widget.onClose,
                            icon: const Icon(
                              Icons.close,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                
                // Menu Items
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.symmetric(vertical: 20),
                    children: _menuItems.map((item) {
                      return _buildMenuItem(item);
                    }).toList(),
                  ),
                ),
                
                // Footer
                Container(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Divider(color: Colors.grey.shade300),
                      const SizedBox(height: 12),
                      _buildMenuItem(
                        SideMenuItem(
                          icon: MdiIcons.logout,
                          title: 'تسجيل الخروج',
                          route: 'logout',
                          color: AppTheme.error,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMenuItem(SideMenuItem item) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: () => widget.onMenuItemTap(item.route),
        borderRadius: AppTheme.mediumRadius,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            borderRadius: AppTheme.mediumRadius,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: (item.color ?? AppTheme.primaryGreen).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  item.icon,
                  color: item.color ?? AppTheme.primaryGreen,
                  size: 20,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  item.title,
                  style: AppTheme.bodyMedium.copyWith(
                    color: item.color ?? AppTheme.textDark,
                  ),
                ),
              ),
              if (item.badge != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.error,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    item.badge!,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  static final List<SideMenuItem> _menuItems = [
    SideMenuItem(
      icon: MdiIcons.fileDocumentOutline,
      title: 'الفواتير',
      route: 'invoices',
    ),
    SideMenuItem(
      icon: MdiIcons.creditCardOutline,
      title: 'إشعار دائن',
      route: 'credit_notes',
    ),
    SideMenuItem(
      icon: MdiIcons.cashCheck,
      title: 'وصولات القبض',
      route: 'payment_receipts',
    ),
    SideMenuItem(
      icon: MdiIcons.bankTransferOut,
      title: 'الحوالات',
      route: 'transfers',
      badge: '3',
    ),
    SideMenuItem(
      icon: MdiIcons.chartBox,
      title: 'التقارير',
      route: 'reports',
    ),
    SideMenuItem(
      icon: MdiIcons.cogOutline,
      title: 'الإعدادات',
      route: 'settings',
    ),
  ];
}

class SideMenuItem {
  final IconData icon;
  final String title;
  final String route;
  final String? badge;
  final Color? color;

  const SideMenuItem({
    required this.icon,
    required this.title,
    required this.route,
    this.badge,
    this.color,
  });
} 