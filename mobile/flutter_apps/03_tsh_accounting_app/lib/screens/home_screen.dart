import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import '../services/api_service.dart';
import '../models/dashboard_stats.dart';
import '../widgets/accounting_equation_widget.dart';
import '../widgets/account_type_pie_chart.dart';
import '../widgets/stat_card.dart';
import 'login_screen.dart';
import 'chart_of_accounts_screen.dart';
import 'journal_entries_screen.dart';

/// Home Screen - Dashboard
/// الشاشة الرئيسية - لوحة التحكم

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _apiService = ApiService();
  DashboardStats? _stats;
  bool _isLoading = true;
  String? _userName;
  String? _userRole;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    _loadDashboardData();
  }

  Future<void> _loadUserInfo() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _userName = prefs.getString(AppConfig.userEmailKey) ?? 'المستخدم';
      _userRole = prefs.getString(AppConfig.userRoleKey) ?? 'محاسب';
    });
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);

    final stats = await _apiService.getDashboardStats();

    setState(() {
      _stats = stats ??
          DashboardStats(
            totalAssets: 1500000,
            totalLiabilities: 800000,
            totalEquity: 700000,
            totalRevenue: 500000,
            totalExpenses: 300000,
            netProfit: 200000,
            workingCapital: 350000,
            cashBalance: 250000,
            totalReceivables: 125430.50,
            totalPayables: 89720.25,
            stockValue: 234890.75,
            totalJournalEntries: 45,
            draftEntries: 5,
            postedEntries: 40,
          );
      _isLoading = false;
    });
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تسجيل الخروج'),
        content: const Text('هل تريد تسجيل الخروج؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('خروج'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _apiService.logout();
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppConfig.appNameAr,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              _userName ?? '',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        backgroundColor: Color(AppConfig.primaryColorValue),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
            tooltip: 'تحديث',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _handleLogout,
            tooltip: 'تسجيل الخروج',
          ),
        ],
      ),
      drawer: _buildDrawer(),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Accounting Equation Widget - المعادلة المحاسبية
                    AccountingEquationWidget(stats: _stats!),
                    const SizedBox(height: 20),

                    // Financial Stats Grid
                    GridView.count(
                      crossAxisCount: 2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.1,
                      children: [
                        StatCard(
                          titleAr: 'صافي الربح',
                          titleEn: 'Net Profit',
                          value: _stats!.netProfit,
                          icon: Icons.trending_up,
                          color: Colors.green,
                        ),
                        StatCard(
                          titleAr: 'رأس المال العامل',
                          titleEn: 'Working Capital',
                          value: _stats!.workingCapital,
                          icon: Icons.account_balance,
                          color: Colors.blue,
                        ),
                        StatCard(
                          titleAr: 'رصيد النقدية',
                          titleEn: 'Cash Balance',
                          value: _stats!.cashBalance,
                          icon: Icons.attach_money,
                          color: Colors.purple,
                        ),
                        StatCard(
                          titleAr: 'قيمة المخزون',
                          titleEn: 'Stock Value',
                          value: _stats!.stockValue,
                          icon: Icons.inventory_2,
                          color: Colors.orange,
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Pie Chart
                    AccountTypePieChart(stats: _stats!),
                    const SizedBox(height: 20),

                    // Receivables & Payables
                    Row(
                      children: [
                        Expanded(
                          child: MiniStatCard(
                            title: 'المدينون',
                            value: _formatCurrency(_stats!.totalReceivables),
                            icon: Icons.arrow_circle_down,
                            color: Colors.green,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: MiniStatCard(
                            title: 'الدائنون',
                            value: _formatCurrency(_stats!.totalPayables),
                            icon: Icons.arrow_circle_up,
                            color: Colors.red,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Journal Entries Summary
                    Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.receipt_long,
                                    color: Color(AppConfig.primaryColorValue)),
                                const SizedBox(width: 8),
                                const Text(
                                  'القيود اليومية',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _buildJournalStat(
                                  'إجمالي',
                                  _stats!.totalJournalEntries.toString(),
                                  Colors.blue,
                                ),
                                _buildJournalStat(
                                  'مسودة',
                                  _stats!.draftEntries.toString(),
                                  Colors.orange,
                                ),
                                _buildJournalStat(
                                  'مرحلة',
                                  _stats!.postedEntries.toString(),
                                  Colors.green,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(AppConfig.primaryColorValue),
                  Color(AppConfig.accentColorValue),
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.person, size: 40, color: Colors.blue),
                ),
                const SizedBox(height: 10),
                Text(
                  _userName ?? '',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  _userRole ?? '',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('لوحة التحكم'),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.account_tree),
            title: const Text('دليل الحسابات'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ChartOfAccountsScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.receipt_long),
            title: const Text('القيود اليومية'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const JournalEntriesScreen(),
                ),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('الإعدادات'),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('تسجيل الخروج',
                style: TextStyle(color: Colors.red)),
            onTap: _handleLogout,
          ),
        ],
      ),
    );
  }

  Widget _buildJournalStat(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  String _formatCurrency(double amount) {
    if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(1)}K';
    } else {
      return amount.toStringAsFixed(0);
    }
  }
}
