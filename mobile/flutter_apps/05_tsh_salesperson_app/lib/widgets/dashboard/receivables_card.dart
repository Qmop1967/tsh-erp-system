import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

import '../../config/app_theme.dart';
import '../common/tsh_card.dart';

class ReceivablesCard extends StatelessWidget {
  final Map<String, dynamic> data;
  final VoidCallback? onTap;

  const ReceivablesCard({
    super.key,
    required this.data,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final total = (data['total'] ?? 0.0).toDouble();
    final regionData = data['byRegion'] as Map<String, dynamic>? ?? {};
    final currency = data['currency'] ?? 'IQD';

    return TSHCard(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.info.withOpacity(0.1),
                    borderRadius: AppTheme.mediumRadius,
                  ),
                  child: Icon(
                    MdiIcons.cashMultiple,
                    color: AppTheme.info,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'المستحقات العامة',
                        style: AppTheme.bodyMedium.copyWith(
                          color: AppTheme.textLight,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'مجموع المبالغ المستحقة لصالح الشركة',
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.textHint,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.chevron_right,
                  color: AppTheme.textLight,
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Total Amount
            Center(
              child: Column(
                children: [
                  Text(
                    NumberFormat.currency(
                      locale: 'ar_IQ',
                      symbol: currency == 'IQD' ? 'د.ع' : '\$',
                      decimalDigits: 0,
                    ).format(total),
                    style: AppTheme.heading1.copyWith(
                      color: AppTheme.info,
                      fontSize: 28,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'إجمالي المستحقات',
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.textLight,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Regional Breakdown
            if (regionData.isNotEmpty) ...[
              Divider(
                color: Colors.grey.shade200,
                thickness: 1,
              ),
              const SizedBox(height: 16),
              Text(
                'التوزيع الجغرافي',
                style: AppTheme.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textDark,
                ),
              ),
              const SizedBox(height: 12),
              ...regionData.entries.take(3).map((entry) {
                final regionName = entry.key;
                final regionAmount = (entry.value['IQD'] ?? 0.0).toDouble();
                
                if (regionAmount <= 0) return const SizedBox.shrink();
                
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: _getRegionColor(regionName),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          regionName,
                          style: AppTheme.bodySmall.copyWith(
                            color: AppTheme.textDark,
                          ),
                        ),
                      ),
                      Text(
                        NumberFormat.currency(
                          locale: 'ar_IQ',
                          symbol: currency == 'IQD' ? 'د.ع' : '\$',
                          decimalDigits: 0,
                        ).format(regionAmount),
                        style: AppTheme.bodySmall.copyWith(
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textDark,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              
              if (regionData.length > 3)
                Container(
                  margin: const EdgeInsets.only(top: 8),
                  child: InkWell(
                    onTap: onTap,
                    borderRadius: AppTheme.mediumRadius,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: AppTheme.info.withOpacity(0.1),
                        borderRadius: AppTheme.mediumRadius,
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'عرض ${regionData.length - 3} منطقة إضافية',
                            style: AppTheme.bodySmall.copyWith(
                              color: AppTheme.info,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Icon(
                            Icons.arrow_forward_ios,
                            size: 12,
                            color: AppTheme.info,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
            
            if (regionData.isEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: AppTheme.mediumRadius,
                ),
                child: Row(
                  children: [
                    Icon(
                      MdiIcons.informationOutline,
                      color: AppTheme.textLight,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'لا توجد مستحقات في الوقت الحالي',
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.textLight,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Color _getRegionColor(String regionName) {
    final colors = [
      AppTheme.primaryGreen,
      AppTheme.info,
      AppTheme.goldAccent,
      AppTheme.success,
      AppTheme.warning,
    ];
    
    final index = regionName.hashCode % colors.length;
    return colors[index.abs()];
  }
} 