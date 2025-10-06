import 'package:flutter/material.dart';

class SimpleDashboard extends StatelessWidget {
  const SimpleDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text(
          'لوحة التحكم',
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: const Color(0xFF1B5E20),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined, color: Colors.white),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.person_outline, color: Colors.white),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Card
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1B5E20), Color(0xFF4CAF50)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'مرحباً بك',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'مندوب المبيعات',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Stats Grid
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.4,
              children: [
                _buildStatCard(
                  'العملاء',
                  '45',
                  Icons.people,
                  const Color(0xFF2196F3),
                ),
                _buildStatCard(
                  'الطلبات',
                  '128',
                  Icons.shopping_cart,
                  const Color(0xFFFF9800),
                ),
                _buildStatCard(
                  'المبيعات',
                  '\$12,500',
                  Icons.attach_money,
                  const Color(0xFF4CAF50),
                ),
                _buildStatCard(
                  'العمولة',
                  '\$281',
                  Icons.account_balance_wallet,
                  const Color(0xFF9C27B0),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Quick Actions
            const Text(
              'الإجراءات السريعة',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildActionButton(
              'عرض العملاء',
              Icons.people,
              () {},
            ),
            const SizedBox(height: 12),
            _buildActionButton(
              'إنشاء طلب جديد',
              Icons.add_shopping_cart,
              () {},
            ),
            const SizedBox(height: 12),
            _buildActionButton(
              'تصفح المنتجات',
              Icons.inventory,
              () {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(String title, IconData icon, VoidCallback onTap) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF1B5E20).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: const Color(0xFF1B5E20)),
        ),
        title: Text(title),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
