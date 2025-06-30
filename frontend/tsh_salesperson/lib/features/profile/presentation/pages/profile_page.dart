import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import '../blocs/profile_bloc.dart';
import '../../../../widgets/language_switcher.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    context.read<ProfileBloc>().add(LoadProfile());
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: BlocListener<ProfileBloc, ProfileState>(
        listener: (context, state) {
          if (state is ProfileError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          } else if (state is PasswordChangeSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Password changed successfully')),
            );
            context.read<ProfileBloc>().add(LoadProfile());
          } else if (state is LogoutSuccess) {
            context.go('/login');
          }
        },
        child: BlocBuilder<ProfileBloc, ProfileState>(
          builder: (context, state) {
            if (state is ProfileLoading) {
              return const Center(child: CircularProgressIndicator());
            } else if (state is ProfileError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 64,
                      color: AppColors.error,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      state.message,
                      style: Theme.of(context).textTheme.titleMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    AppButton(
                      text: 'Retry',
                      onPressed: () => context.read<ProfileBloc>().add(LoadProfile()),
                    ),
                  ],
                ),
              );
            } else if (state is ProfileLoaded) {
              return CustomScrollView(
                slivers: [
                  _buildAppBar(state),
                  _buildTabBar(),
                  _buildTabBarView(state),
                ],
              );
            }

            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }

  Widget _buildAppBar(ProfileLoaded state) {
    return SliverAppBar(
      expandedHeight: 280,
      pinned: true,
      backgroundColor: AppColors.primary,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                AppColors.primary,
                AppColors.primary.withValues(alpha: 0.8),
              ],
            ),
          ),
          child: SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 40),
                CircleAvatar(
                  radius: 50,
                  backgroundColor: Colors.white.withValues(alpha: 0.2),
                  child: Text(
                    state.user.fullName.split(' ').map((e) => e[0]).take(2).join(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  state.user.fullName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  state.user.role?.toString() ?? 'Travel Salesperson',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.9),
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  state.user.email,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit, color: Colors.white),
          onPressed: () => _showEditProfileDialog(state.user),
        ),
      ],
    );
  }

  Widget _buildTabBar() {
    return SliverPersistentHeader(
      pinned: true,
      delegate: _SliverTabBarDelegate(
        TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          tabs: const [
            Tab(text: 'Stats'),
            Tab(text: 'Settings'),
            Tab(text: 'Account'),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBarView(ProfileLoaded state) {
    return SliverFillRemaining(
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildStatsTab(state.stats),
          _buildSettingsTab(state.settings),
          _buildAccountTab(state.user),
        ],
      ),
    );
  }

  Widget _buildStatsTab(ProfileStats stats) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  title: 'Total Sales',
                  value: stats.totalSales.toString(),
                  icon: Icons.shopping_cart,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  title: 'Revenue',
                  value: '\$${stats.totalRevenue.toStringAsFixed(0)}',
                  icon: Icons.attach_money,
                  color: AppColors.success,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  title: 'Active Customers',
                  value: stats.activeCustomers.toString(),
                  icon: Icons.people,
                  color: AppColors.info,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  title: 'Orders This Month',
                  value: stats.ordersThisMonth.toString(),
                  icon: Icons.calendar_today,
                  color: AppColors.warning,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  title: 'Avg Order Value',
                  value: '\$${stats.averageOrderValue.toStringAsFixed(0)}',
                  icon: Icons.trending_up,
                  color: AppColors.secondary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  title: 'Days Active',
                  value: stats.daysActive.toString(),
                  icon: Icons.star,
                  color: AppColors.accent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          AppCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Performance Overview',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildPerformanceItem(
                    'Sales Target Achievement',
                    '87%',
                    0.87,
                    AppColors.success,
                  ),
                  const SizedBox(height: 12),
                  _buildPerformanceItem(
                    'Customer Satisfaction',
                    '94%',
                    0.94,
                    AppColors.primary,
                  ),
                  const SizedBox(height: 12),
                  _buildPerformanceItem(
                    'Monthly Growth',
                    '12%',
                    0.12,
                    AppColors.warning,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return AppCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 16),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceItem(String title, String value, double progress, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title),
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: color.withValues(alpha: 0.2),
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }
  
  Widget _buildSettingsTab(ProfileSettings settings) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Language Switcher
          const LanguageSwitcher(),
          const SizedBox(height: 16),
          
          AppCard(
            child: Column(
              children: [
                _buildSettingsTile(
                  title: 'Notifications',
                  subtitle: 'Receive push notifications',
                  trailing: Switch(
                    value: settings.notifications,
                    onChanged: (value) {
                      final updatedSettings = settings.copyWith(notifications: value);
                      context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                    },
                  ),
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Dark Mode',
                  subtitle: 'Use dark theme',
                  trailing: Switch(
                    value: settings.darkMode,
                    onChanged: (value) {
                      final updatedSettings = settings.copyWith(darkMode: value);
                      context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                    },
                  ),
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Location Tracking',
                  subtitle: 'Track location for delivery',
                  trailing: Switch(
                    value: settings.locationTracking,
                    onChanged: (value) {
                      final updatedSettings = settings.copyWith(locationTracking: value);
                      context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                    },
                  ),
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Offline Sync',
                  subtitle: 'Sync data when offline',
                  trailing: Switch(
                    value: settings.offlineSync,
                    onChanged: (value) {
                      final updatedSettings = settings.copyWith(offlineSync: value);
                      context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                    },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          AppCard(
            child: Column(
              children: [
                _buildSettingsTile(
                  title: 'Language',
                  subtitle: settings.language,
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () => _showLanguageDialog(settings),
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Currency',
                  subtitle: settings.currency,
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () => _showCurrencyDialog(settings),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAccountTab(User user) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          AppCard(
            child: Column(
              children: [
                _buildSettingsTile(
                  title: 'Change Password',
                  subtitle: 'Update your password',
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: _showChangePasswordDialog,
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Privacy Policy',
                  subtitle: 'Read our privacy policy',
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    // Navigate to privacy policy
                  },
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Terms of Service',
                  subtitle: 'Read our terms of service',
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    // Navigate to terms of service
                  },
                ),
                const Divider(),
                _buildSettingsTile(
                  title: 'Help & Support',
                  subtitle: 'Get help or contact support',
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    // Navigate to help & support
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          AppButton(
            text: 'Logout',
            customColor: AppColors.error,
            onPressed: () => _showLogoutConfirmation(),
          ),
          const SizedBox(height: 16),
          Text(
            'Version 1.0.0',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsTile({
    required String title,
    required String subtitle,
    required Widget trailing,
    VoidCallback? onTap,
  }) {
    return ListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: trailing,
      onTap: onTap,
    );
  }

  void _showEditProfileDialog(User user) {
    final nameController = TextEditingController(text: user.fullName);
    final emailController = TextEditingController(text: user.email);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AppTextField(
              controller: nameController,
              hint: 'Full Name',
              prefixIcon: Icon(Icons.person),
            ),
            const SizedBox(height: 16),
            AppTextField(
              controller: emailController,
              hint: 'Email',
              prefixIcon: Icon(Icons.email),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton(
            text: 'Update',
            onPressed: () {
              if (nameController.text.isNotEmpty && emailController.text.isNotEmpty) {
                // For simplicity, we'll keep the same first/last name structure
                final nameParts = nameController.text.split(' ');
                final firstName = nameParts.isNotEmpty ? nameParts.first : user.firstName;
                final lastName = nameParts.length > 1 ? nameParts.sublist(1).join(' ') : user.lastName;
                
                final updatedUser = user.copyWith(
                  firstName: firstName,
                  lastName: lastName,
                  email: emailController.text,
                );
                context.read<ProfileBloc>().add(UpdateProfile(updatedUser));
                Navigator.of(context).pop();
              }
            },
          ),
        ],
      ),
    );
  }

  void _showChangePasswordDialog() {
    final currentPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Change Password'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AppTextField(
              controller: currentPasswordController,
              hint: 'Current Password',
              prefixIcon: Icon(Icons.lock),
              obscureText: true,
            ),
            const SizedBox(height: 16),
            AppTextField(
              controller: newPasswordController,
              hint: 'New Password',
              prefixIcon: Icon(Icons.lock_outline),
              obscureText: true,
            ),
            const SizedBox(height: 16),
            AppTextField(
              controller: confirmPasswordController,
              hint: 'Confirm New Password',
              prefixIcon: Icon(Icons.lock_outline),
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton(
            text: 'Change',
            onPressed: () {
              if (currentPasswordController.text.isNotEmpty &&
                  newPasswordController.text.isNotEmpty &&
                  newPasswordController.text == confirmPasswordController.text) {
                context.read<ProfileBloc>().add(ChangePassword(
                  currentPassword: currentPasswordController.text,
                  newPassword: newPasswordController.text,
                ));
                Navigator.of(context).pop();
              }
            },
          ),
        ],
      ),
    );
  }

  void _showLanguageDialog(ProfileSettings settings) {
    final languages = ['English', 'Arabic', 'Hindi', 'Urdu'];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: languages.map((language) {
            return RadioListTile<String>(
              title: Text(language),
              value: language,
              groupValue: settings.language,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = settings.copyWith(language: value);
                  context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                  Navigator.of(context).pop();
                }
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  void _showCurrencyDialog(ProfileSettings settings) {
    final currencies = ['AED', 'USD', 'EUR', 'GBP'];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Currency'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: currencies.map((currency) {
            return RadioListTile<String>(
              title: Text(currency),
              value: currency,
              groupValue: settings.currency,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = settings.copyWith(currency: value);
                  context.read<ProfileBloc>().add(UpdateSettings(updatedSettings));
                  Navigator.of(context).pop();
                }
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  void _showLogoutConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton(
            text: 'Logout',
            customColor: AppColors.error,
            onPressed: () {
              Navigator.of(context).pop();
              context.read<ProfileBloc>().add(LogoutUser());
            },
          ),
        ],
      ),
    );
  }
}

class _SliverTabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar _tabBar;

  _SliverTabBarDelegate(this._tabBar);

  @override
  double get minExtent => _tabBar.preferredSize.height;

  @override
  double get maxExtent => _tabBar.preferredSize.height;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: Colors.white,
      child: _tabBar,
    );
  }

  @override
  bool shouldRebuild(_SliverTabBarDelegate oldDelegate) {
    return false;
  }
}
