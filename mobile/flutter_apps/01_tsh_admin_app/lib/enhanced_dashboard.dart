import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import 'enhanced_localization.dart';

class EnhancedExecutiveDashboardScreen extends StatefulWidget {
  const EnhancedExecutiveDashboardScreen({super.key});

  @override
  State<EnhancedExecutiveDashboardScreen> createState() => _EnhancedExecutiveDashboardScreenState();
}

class _EnhancedExecutiveDashboardScreenState extends State<EnhancedExecutiveDashboardScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  
  // Mock data - replace with real API calls
  final Map<String, dynamic> _dashboardData = {
    'financial': {
      'available_cash': 125750000,
      'total_receivables': 89520000,
      'total_payables': 234560000,
      'inventory_valuation': 456890000,
      'net_profit': 45230000,
      'gross_margin': 23.5,
      'cash_flow': 12340000,
      'budget_variance': -2.3,
    },
    'operations': {
      'active_orders': 127,
      'pending_deliveries': 43,
      'inventory_alerts': 8,
      'customer_satisfaction': 94.2,
      'supplier_performance': 87.6,
      'production_efficiency': 92.1,
    },
    'hr': {
      'total_employees': 248,
      'active_employees': 242,
      'departments': 12,
      'attendance_rate': 96.8,
      'payroll_pending': 3,
      'training_sessions': 14,
      'performance_reviews': 89,
    },
    'system': {
      'uptime': 99.97,
      'database_status': 'healthy',
      'backup_status': 'completed',
      'security_alerts': 0,
      'api_performance': 245,
      'active_sessions': 67,
    }
  };

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut)
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = EnhancedTSHLocalizations.of(context)!;
    final languageService = Provider.of<EnhancedLanguageService>(context);

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _refreshDashboard,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Section
                _buildDashboardHeader(localizations, languageService),
                const SizedBox(height: 20),
                
                // Quick Stats Row
                _buildQuickStatsRow(localizations),
                const SizedBox(height: 20),
                
                // Financial Metrics Section
                _buildFinancialSection(localizations),
                const SizedBox(height: 20),
                
                // Operations Section
                _buildOperationsSection(localizations),
                const SizedBox(height: 20),
                
                // HR Section
                _buildHRSection(localizations),
                const SizedBox(height: 20),
                
                // System Status Section
                _buildSystemSection(localizations),
                const SizedBox(height: 20),
                
                // Recent Activities
                _buildRecentActivities(localizations),
                const SizedBox(height: 20),
                
                // Quick Actions
                _buildQuickActions(localizations),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDashboardHeader(EnhancedTSHLocalizations localizations, EnhancedLanguageService languageService) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            TSHTheme.primaryTeal,
            TSHTheme.primaryTeal.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: TSHTheme.primaryTeal.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: languageService.isRTL 
                  ? CrossAxisAlignment.end 
                  : CrossAxisAlignment.start,
              children: [
                Text(
                  localizations.translate('welcome_admin'),
                  style: TSHTheme.headingLarge.copyWith(
                    color: TSHTheme.surfaceWhite,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  localizations.translate('executive_summary'),
                  style: TSHTheme.bodyLarge.copyWith(
                    color: TSHTheme.surfaceWhite.withOpacity(0.9),
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: TSHTheme.surfaceWhite.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.calendar_today, 
                          color: TSHTheme.surfaceWhite, size: 16),
                      const SizedBox(width: 8),
                      Text(
                        '${localizations.translate('today_date')}: ${_formatDate(DateTime.now())}',
                        style: TSHTheme.bodySmall.copyWith(
                          color: TSHTheme.surfaceWhite,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: TSHTheme.surfaceWhite.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.dashboard_rounded,
              color: TSHTheme.surfaceWhite,
              size: 48,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStatsRow(EnhancedTSHLocalizations localizations) {
    return Row(
      children: [
        Expanded(
          child: _buildQuickStatCard(
            Icons.trending_up,
            localizations.translate('net_profit'),
            _formatCurrency(_dashboardData['financial']['net_profit']),
            TSHTheme.successGreen,
            '+12.5%',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickStatCard(
            Icons.people,
            localizations.translate('active_employees'),
            '${_dashboardData['hr']['active_employees']}',
            TSHTheme.primaryBlue,
            '96.8%',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickStatCard(
            Icons.inventory,
            localizations.translate('inventory_alerts'),
            '${_dashboardData['operations']['inventory_alerts']}',
            TSHTheme.warningOrange,
            'Alert',
          ),
        ),
      ],
    );
  }

  Widget _buildQuickStatCard(IconData icon, String title, String value, Color color, String change) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const Spacer(),
              Text(
                change,
                style: TSHTheme.bodySmall.copyWith(
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: TSHTheme.headingMedium.copyWith(
              color: TSHTheme.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TSHTheme.bodySmall.copyWith(
              color: TSHTheme.textSecondary,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialSection(EnhancedTSHLocalizations localizations) {
    return _buildSection(
      localizations.translate('financial_metrics'),
      Icons.account_balance_wallet,
      [
        _buildMetricCard(
          localizations.translate('available_cash'),
          _formatCurrency(_dashboardData['financial']['available_cash']),
          Icons.account_balance_wallet,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('total_receivables'),
          _formatCurrency(_dashboardData['financial']['total_receivables']),
          Icons.trending_up,
          TSHTheme.primaryBlue,
        ),
        _buildMetricCard(
          localizations.translate('total_payables'),
          _formatCurrency(_dashboardData['financial']['total_payables']),
          Icons.trending_down,
          TSHTheme.warningOrange,
        ),
        _buildMetricCard(
          localizations.translate('inventory_valuation'),
          _formatCurrency(_dashboardData['financial']['inventory_valuation']),
          Icons.inventory,
          TSHTheme.primaryTeal,
        ),
      ],
    );
  }

  Widget _buildOperationsSection(EnhancedTSHLocalizations localizations) {
    return _buildSection(
      localizations.translate('operations_overview'),
      Icons.business_center,
      [
        _buildMetricCard(
          localizations.translate('active_orders'),
          '${_dashboardData['operations']['active_orders']}',
          Icons.shopping_cart,
          TSHTheme.primaryBlue,
        ),
        _buildMetricCard(
          localizations.translate('pending_deliveries'),
          '${_dashboardData['operations']['pending_deliveries']}',
          Icons.local_shipping,
          TSHTheme.warningOrange,
        ),
        _buildMetricCard(
          localizations.translate('customer_satisfaction'),
          '${_dashboardData['operations']['customer_satisfaction']}%',
          Icons.sentiment_very_satisfied,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('production_efficiency'),
          '${_dashboardData['operations']['production_efficiency']}%',
          Icons.precision_manufacturing,
          TSHTheme.primaryTeal,
        ),
      ],
    );
  }

  Widget _buildHRSection(EnhancedTSHLocalizations localizations) {
    return _buildSection(
      localizations.translate('hr_management'),
      Icons.people,
      [
        _buildMetricCard(
          localizations.translate('total_employees'),
          '${_dashboardData['hr']['total_employees']}',
          Icons.people,
          TSHTheme.primaryBlue,
        ),
        _buildMetricCard(
          localizations.translate('attendance_rate'),
          '${_dashboardData['hr']['attendance_rate']}%',
          Icons.access_time,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('training_sessions'),
          '${_dashboardData['hr']['training_sessions']}',
          Icons.school,
          TSHTheme.warningOrange,
        ),
        _buildMetricCard(
          localizations.translate('performance_reviews'),
          '${_dashboardData['hr']['performance_reviews']}',
          Icons.assessment,
          TSHTheme.primaryTeal,
        ),
      ],
    );
  }

  Widget _buildSystemSection(EnhancedTSHLocalizations localizations) {
    return _buildSection(
      localizations.translate('system_status'),
      Icons.settings,
      [
        _buildMetricCard(
          localizations.translate('system_uptime'),
          '${_dashboardData['system']['uptime']}%',
          Icons.trending_up,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('database_status'),
          localizations.translate('healthy'),
          Icons.storage,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('security_alerts'),
          '${_dashboardData['system']['security_alerts']}',
          Icons.security,
          TSHTheme.successGreen,
        ),
        _buildMetricCard(
          localizations.translate('user_sessions'),
          '${_dashboardData['system']['active_sessions']}',
          Icons.person,
          TSHTheme.primaryBlue,
        ),
      ],
    );
  }

  Widget _buildSection(String title, IconData icon, List<Widget> cards) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: TSHTheme.primaryTeal.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: TSHTheme.primaryTeal, size: 20),
            ),
            const SizedBox(width: 12),
            Text(
              title,
              style: TSHTheme.headingMedium.copyWith(
                color: TSHTheme.textPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.5,
          children: cards,
        ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const Spacer(),
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TSHTheme.headingSmall.copyWith(
              color: TSHTheme.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: TSHTheme.bodySmall.copyWith(
              color: TSHTheme.textSecondary,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivities(EnhancedTSHLocalizations localizations) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: TSHTheme.primaryTeal.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            localizations.translate('recent_activities'),
            style: TSHTheme.headingMedium.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ...List.generate(3, (index) => _buildActivityItem(
            Icons.trending_up,
            'New sales order #SO-${1000 + index}',
            '2 hours ago',
            TSHTheme.successGreen,
          )),
        ],
      ),
    );
  }

  Widget _buildActivityItem(IconData icon, String title, String time, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TSHTheme.bodyMedium.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  time,
                  style: TSHTheme.bodySmall.copyWith(
                    color: TSHTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(EnhancedTSHLocalizations localizations) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: TSHTheme.primaryTeal.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            localizations.translate('quick_actions'),
            style: TSHTheme.headingMedium.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 3,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.2,
            children: [
              _buildActionButton(
                Icons.analytics,
                localizations.translate('generate_report'),
                TSHTheme.primaryBlue,
              ),
              _buildActionButton(
                Icons.backup,
                localizations.translate('backup_system'),
                TSHTheme.successGreen,
              ),
              _buildActionButton(
                Icons.people,
                localizations.translate('user_management'),
                TSHTheme.warningOrange,
              ),
              _buildActionButton(
                Icons.file_download,
                localizations.translate('export_data'),
                TSHTheme.primaryTeal,
              ),
              _buildActionButton(
                Icons.file_upload,
                localizations.translate('import_data'),
                TSHTheme.primaryBlue,
              ),
              _buildActionButton(
                Icons.build,
                localizations.translate('system_maintenance'),
                TSHTheme.warningOrange,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(IconData icon, String label, Color color) {
    return InkWell(
      onTap: () => _handleQuickAction(label),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: color.withOpacity(0.2)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(
              label,
              style: TSHTheme.bodySmall.copyWith(
                color: color,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _refreshDashboard() async {
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    setState(() {
      // Update data
    });
  }

  void _handleQuickAction(String action) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Opening $action...'),
        backgroundColor: TSHTheme.primaryTeal,
      ),
    );
  }

  String _formatCurrency(double amount) {
    if (amount >= 1000000000) {
      return '${(amount / 1000000000).toStringAsFixed(1)}B IQD';
    } else if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M IQD';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(1)}K IQD';
    }
    return '${amount.toStringAsFixed(0)} IQD';
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
