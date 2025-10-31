import 'package:flutter/material.dart';
import '../models/dashboard_stats.dart';
import '../config/app_config.dart';

/// Accounting Equation Widget
/// عنصر المعادلة المحاسبية التفاعلي
/// الأصول = الخصوم + حقوق الملكية

class AccountingEquationWidget extends StatefulWidget {
  final DashboardStats stats;
  final bool showAnimation;

  const AccountingEquationWidget({
    Key? key,
    required this.stats,
    this.showAnimation = true,
  }) : super(key: key);

  @override
  State<AccountingEquationWidget> createState() =>
      _AccountingEquationWidgetState();
}

class _AccountingEquationWidgetState extends State<AccountingEquationWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    _scaleAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    );

    if (widget.showAnimation) {
      _controller.forward();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isBalanced = widget.stats.isAccountingEquationBalanced;

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.blue[50]!,
              Colors.purple[50]!,
            ],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Title with Balance Indicator
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.calculate_outlined,
                      color: Color(AppConfig.primaryColorValue),
                      size: 28,
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'المعادلة المحاسبية',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Color(AppConfig.primaryColorValue),
                          ),
                        ),
                        const Text(
                          'Accounting Equation',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                // Balance Indicator
                ScaleTransition(
                  scale: _scaleAnimation,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: isBalanced ? Colors.green : Colors.orange,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          isBalanced ? Icons.check_circle : Icons.warning,
                          color: Colors.white,
                          size: 16,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          isBalanced ? 'متوازنة' : 'غير متوازنة',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Equation Visualization
            Row(
              children: [
                // Left Side: Assets
                Expanded(
                  flex: 5,
                  child: _buildEquationBox(
                    title: 'الأصول',
                    subtitle: 'Assets',
                    amount: widget.stats.totalAssets,
                    color: Color(AppConfig.assetColorValue),
                    icon: Icons.account_balance_wallet,
                  ),
                ),
                // Equals Sign
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: ScaleTransition(
                    scale: _scaleAnimation,
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: isBalanced ? Colors.green : Colors.orange,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.drag_handle,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                  ),
                ),
                // Right Side: Liabilities + Equity
                Expanded(
                  flex: 5,
                  child: Column(
                    children: [
                      _buildEquationBox(
                        title: 'الخصوم',
                        subtitle: 'Liabilities',
                        amount: widget.stats.totalLiabilities,
                        color: Color(AppConfig.liabilityColorValue),
                        icon: Icons.credit_card,
                        isSmall: true,
                      ),
                      const SizedBox(height: 8),
                      // Plus Sign
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.grey[300],
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.add,
                          size: 16,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildEquationBox(
                        title: 'حقوق الملكية',
                        subtitle: 'Equity',
                        amount: widget.stats.totalEquity,
                        color: Color(AppConfig.equityColorValue),
                        icon: Icons.person_outline,
                        isSmall: true,
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Total Comparison
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isBalanced ? Colors.green : Colors.orange,
                  width: 2,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildTotalColumn(
                    'الجانب الأيسر',
                    'Left Side',
                    widget.stats.totalAssets,
                    Color(AppConfig.assetColorValue),
                  ),
                  Container(
                    height: 40,
                    width: 2,
                    color: Colors.grey[300],
                  ),
                  _buildTotalColumn(
                    'الجانب الأيمن',
                    'Right Side',
                    widget.stats.totalLiabilities + widget.stats.totalEquity,
                    Color(AppConfig.primaryColorValue),
                  ),
                  Container(
                    height: 40,
                    width: 2,
                    color: Colors.grey[300],
                  ),
                  _buildTotalColumn(
                    'الفرق',
                    'Difference',
                    (widget.stats.totalAssets -
                            (widget.stats.totalLiabilities +
                                widget.stats.totalEquity))
                        .abs(),
                    isBalanced ? Colors.green : Colors.orange,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEquationBox({
    required String title,
    required String subtitle,
    required double amount,
    required Color color,
    required IconData icon,
    bool isSmall = false,
  }) {
    return Container(
      padding: EdgeInsets.all(isSmall ? 12 : 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: color, width: 2),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: isSmall ? 24 : 32),
          SizedBox(height: isSmall ? 4 : 8),
          Text(
            title,
            style: TextStyle(
              fontSize: isSmall ? 12 : 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: isSmall ? 8 : 10,
              color: Colors.grey,
            ),
          ),
          SizedBox(height: isSmall ? 4 : 8),
          Text(
            _formatCurrency(amount),
            style: TextStyle(
              fontSize: isSmall ? 14 : 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildTotalColumn(
      String title, String subtitle, double amount, Color color) {
    return Column(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          subtitle,
          style: const TextStyle(
            fontSize: 8,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          _formatCurrency(amount),
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
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
