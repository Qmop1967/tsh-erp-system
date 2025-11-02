import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../utils/tsh_theme.dart';
import 'auth_screen.dart';
import 'orders_screen.dart';

final userProvider = FutureProvider<User?>((ref) async {
  try {
    final token = await ApiService.getAuthToken();
    if (token == null) return null;
    return await ApiService.getUserProfile();
  } catch (e) {
    return null;
  }
});

class AccountScreen extends ConsumerStatefulWidget {
  const AccountScreen({super.key});

  @override
  ConsumerState<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends ConsumerState<AccountScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final userAsync = ref.watch(userProvider);

    return Scaffold(
      backgroundColor: TSHTheme.backgroundLight,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: const Text(
          'حسابي',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: TSHTheme.textPrimary,
          ),
        ),
        centerTitle: true,
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: userAsync.when(
          data: (user) {
            if (user == null) {
              return _buildGuestView(context);
            }
            return _buildAuthenticatedView(context, user);
          },
          loading: () => _buildLoadingState(),
          error: (error, stack) => _buildGuestView(context),
        ),
      ),
    );
  }

  Widget _buildAuthenticatedView(BuildContext context, User user) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // Profile header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: const BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black12,
                  blurRadius: 8,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                // Avatar
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [
                        TSHTheme.primary,
                        TSHTheme.accent,
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: TSHTheme.primary.withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.person,
                    size: 50,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),

                // Name
                Text(
                  user.fullName ?? user.email.split('@')[0] ?? 'مستخدم',
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: TSHTheme.textPrimary,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),

                // Email
                Text(
                  user.email,
                  style: TextStyle(
                    fontSize: 15,
                    color: TSHTheme.mutedForeground,
                  ),
                  textAlign: TextAlign.center,
                ),
                if (user.phone != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    user.phone!,
                    style: TextStyle(
                      fontSize: 14,
                      color: TSHTheme.mutedForeground,
                    ),
                  ),
                ],
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Menu items
          _buildMenuSection(
            context,
            'الطلبات والمشتريات',
            [
              _buildMenuItem(
                context,
                icon: Icons.receipt_long_outlined,
                title: 'طلباتي',
                subtitle: 'عرض جميع الطلبات السابقة',
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const OrdersScreen(),
                    ),
                  );
                },
              ),
              _buildMenuItem(
                context,
                icon: Icons.favorite_outline,
                title: 'المفضلة',
                subtitle: 'المنتجات المحفوظة',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('قريباً...')),
                  );
                },
                trailing: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'قريباً',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Colors.orange[800],
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          _buildMenuSection(
            context,
            'الإعدادات',
            [
              _buildMenuItem(
                context,
                icon: Icons.person_outline,
                title: 'تعديل الملف الشخصي',
                subtitle: 'تحديث المعلومات الشخصية',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('قريباً...')),
                  );
                },
              ),
              _buildMenuItem(
                context,
                icon: Icons.notifications_outlined,
                title: 'الإشعارات',
                subtitle: 'إدارة الإشعارات',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('قريباً...')),
                  );
                },
              ),
              _buildMenuItem(
                context,
                icon: Icons.language,
                title: 'اللغة',
                subtitle: 'العربية',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('قريباً...')),
                  );
                },
              ),
            ],
          ),

          const SizedBox(height: 16),

          _buildMenuSection(
            context,
            'الدعم',
            [
              _buildMenuItem(
                context,
                icon: Icons.help_outline,
                title: 'المساعدة والدعم',
                subtitle: 'الأسئلة الشائعة',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('قريباً...')),
                  );
                },
              ),
              _buildMenuItem(
                context,
                icon: Icons.info_outline,
                title: 'حول التطبيق',
                subtitle: 'الإصدار 1.0.0',
                onTap: () {
                  _showAboutDialog(context);
                },
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Logout button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _handleLogout(context),
                icon: const Icon(Icons.logout),
                label: const Text(
                  'تسجيل الخروج',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: TSHTheme.destructive,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 2,
                ),
              ),
            ),
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildGuestView(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            Container(
              width: 140,
              height: 140,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [
                    TSHTheme.primary.withOpacity(0.1),
                    TSHTheme.accent.withOpacity(0.1),
                  ],
                ),
              ),
              child: const Icon(
                Icons.person_outline,
                size: 70,
                color: TSHTheme.primary,
              ),
            ),
            const SizedBox(height: 32),

            // Title
            const Text(
              'مرحباً بك في TSH',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: TSHTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 12),

            // Subtitle
            Text(
              'سجل الدخول للاستمتاع بتجربة تسوق مخصصة',
              style: TextStyle(
                fontSize: 16,
                color: TSHTheme.mutedForeground,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),

            // Features list
            _buildFeatureItem(
              Icons.receipt_long_outlined,
              'تتبع طلباتك',
              'راقب حالة طلباتك في الوقت الفعلي',
            ),
            const SizedBox(height: 20),
            _buildFeatureItem(
              Icons.favorite_outline,
              'حفظ المفضلات',
              'احفظ منتجاتك المفضلة للرجوع إليها لاحقاً',
            ),
            const SizedBox(height: 20),
            _buildFeatureItem(
              Icons.local_offer_outlined,
              'عروض حصرية',
              'احصل على عروض وخصومات خاصة',
            ),
            const SizedBox(height: 48),

            // Login button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _navigateToAuth(context, isLogin: true),
                icon: const Icon(Icons.login),
                label: const Text(
                  'تسجيل الدخول',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: TSHTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 4,
                  shadowColor: TSHTheme.primary.withOpacity(0.4),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Register button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _navigateToAuth(context, isLogin: false),
                icon: const Icon(Icons.person_add_outlined),
                label: const Text(
                  'إنشاء حساب جديد',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: OutlinedButton.styleFrom(
                  foregroundColor: TSHTheme.primary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  side: const BorderSide(color: TSHTheme.primary, width: 2),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Guest continue
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text(
                'المتابعة كضيف',
                style: TextStyle(
                  fontSize: 14,
                  color: TSHTheme.mutedForeground,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String subtitle) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                TSHTheme.primary.withOpacity(0.1),
                TSHTheme.accent.withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, size: 28, color: TSHTheme.primary),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: TSHTheme.textPrimary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 13,
                  color: TSHTheme.mutedForeground,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMenuSection(BuildContext context, String title, List<Widget> items) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: TSHTheme.mutedForeground,
                letterSpacing: 0.5,
              ),
            ),
          ),
          ...items,
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    Widget? trailing,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      TSHTheme.primary.withOpacity(0.1),
                      TSHTheme.accent.withOpacity(0.1),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 22, color: TSHTheme.primary),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: TSHTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 13,
                        color: TSHTheme.mutedForeground,
                      ),
                    ),
                  ],
                ),
              ),
              trailing ??
                  Icon(
                    Icons.arrow_back_ios,
                    size: 16,
                    color: TSHTheme.mutedForeground,
                  ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: CircularProgressIndicator(
        color: TSHTheme.primary,
      ),
    );
  }

  void _navigateToAuth(BuildContext context, {required bool isLogin}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AuthScreen(),
      ),
    ).then((_) {
      // Refresh user data after auth
      ref.invalidate(userProvider);
    });
  }

  void _handleLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: const Text(
          'تسجيل الخروج',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: TSHTheme.textPrimary,
          ),
        ),
        content: const Text(
          'هل أنت متأكد من تسجيل الخروج؟',
          style: TextStyle(
            color: TSHTheme.textPrimary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'إلغاء',
              style: TextStyle(
                color: TSHTheme.mutedForeground,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              await ApiService.clearAuthToken();
              ref.invalidate(userProvider);
              if (context.mounted) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم تسجيل الخروج بنجاح'),
                    backgroundColor: TSHTheme.success,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: TSHTheme.destructive,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('تسجيل الخروج'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [TSHTheme.primary, TSHTheme.accent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.shopping_bag,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'تطبيق TSH',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: TSHTheme.textPrimary,
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'الإصدار: 1.0.0',
              style: TextStyle(
                fontSize: 14,
                color: TSHTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'تطبيق التسوق الإلكتروني من TSH',
              style: TextStyle(
                fontSize: 14,
                color: TSHTheme.mutedForeground,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              '© 2025 TSH. جميع الحقوق محفوظة.',
              style: TextStyle(
                fontSize: 12,
                color: TSHTheme.mutedForeground,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إغلاق'),
          ),
        ],
      ),
    );
  }
}
