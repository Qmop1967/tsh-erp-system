import 'package:flutter/material.dart';
import '../../../../localization/app_localizations.dart';

class AlertsPage extends StatelessWidget {
  const AlertsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                localizations.fraudAlerts,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                isArabic 
                    ? 'تنبيهات الأمان ومنع الاحتيال'
                    : 'Security alerts and fraud prevention notifications',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 24),
              
              // Critical Alert Example
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تنبيه بالغ الأهمية: تحويل مشبوه'
                    : 'Critical Alert: Suspicious Transfer',
                subtitle: isArabic
                    ? 'تم اكتشاف تضارب في العمولة - انتباه فوري مطلوب'
                    : 'Commission discrepancy detected - immediate attention required',
                icon: Icons.error,
                color: Colors.red,
                time: '5 min ago',
              ),
              
              const SizedBox(height: 12),
              
              // Warning Alert
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تحذير: دقة الموقع منخفضة'
                    : 'Warning: Low GPS Accuracy',
                subtitle: isArabic
                    ? 'تحقق من إعدادات الموقع للحصول على تتبع أفضل'
                    : 'Check location settings for better tracking accuracy',
                icon: Icons.location_off,
                color: Colors.orange,
                time: '15 min ago',
              ),
              
              const SizedBox(height: 12),
              
              // Info Alert
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تم التحقق من التحويل بنجاح'
                    : 'Transfer Verified Successfully',
                subtitle: isArabic
                    ? 'تحويل بقيمة 1,250,000 د.ع تم التحقق منه'
                    : 'Transfer of 1,250,000 IQD has been verified',
                icon: Icons.check_circle,
                color: Colors.green,
                time: '1 hour ago',
              ),
              
              const Spacer(),
              
              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        // Refresh alerts
                      },
                      icon: const Icon(Icons.refresh),
                      label: Text(
                        isArabic ? 'تحديث التنبيهات' : 'Refresh Alerts',
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1565C0),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        // Mark all as read
                      },
                      icon: const Icon(Icons.done_all),
                      label: Text(
                        isArabic ? 'تعليم كمقروء' : 'Mark All Read',
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildAlertCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String time,
  }) {
    return Card(
      elevation: 2,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(subtitle),
            const SizedBox(height: 4),
            Text(
              time,
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 12,
              ),
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.more_vert),
          onPressed: () {
            // Show alert options
          },
        ),
        isThreeLine: true,
      ),
    );
  }
} 