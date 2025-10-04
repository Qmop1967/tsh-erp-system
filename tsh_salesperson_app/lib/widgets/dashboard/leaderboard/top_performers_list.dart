import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:shimmer/shimmer.dart';
import 'package:intl/intl.dart';

import '../../../config/app_theme.dart';

class TopPerformersList extends StatelessWidget {
  final Map<String, dynamic>? leaderboardData;
  final bool isLoading;

  const TopPerformersList({
    super.key,
    this.leaderboardData,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _buildShimmer();
    }

    final topPerformers = leaderboardData?['top_performers'] ?? [];

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  gradient: AppTheme.goldGradient,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  MdiIcons.accountStar,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'أفضل المندوبين',
                style: TextStyle(
                  color: AppTheme.textDark,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (topPerformers.isEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text(
                  'لا توجد بيانات',
                  style: TextStyle(
                    color: AppTheme.textLight,
                    fontSize: 14,
                  ),
                ),
              ),
            )
          else
            ...topPerformers.asMap().entries.map((entry) {
              final index = entry.key;
              final performer = entry.value;
              return _buildPerformerItem(
                rank: index + 1,
                name: performer['name'] ?? 'مندوب',
                sales: performer['sales'] ?? 0.0,
                collections: performer['collections'] ?? 0.0,
                isCurrentUser: performer['is_current_user'] ?? false,
              );
            }).toList(),
        ],
      ),
    );
  }

  Widget _buildPerformerItem({
    required int rank,
    required String name,
    required double sales,
    required double collections,
    required bool isCurrentUser,
  }) {
    Color rankColor;
    IconData rankIcon;
    
    if (rank == 1) {
      rankColor = const Color(0xFFFFD700); // Gold
      rankIcon = MdiIcons.trophy;
    } else if (rank == 2) {
      rankColor = const Color(0xFFC0C0C0); // Silver
      rankIcon = MdiIcons.medal;
    } else if (rank == 3) {
      rankColor = const Color(0xFFCD7F32); // Bronze
      rankIcon = MdiIcons.medal;
    } else {
      rankColor = AppTheme.textLight;
      rankIcon = MdiIcons.accountCircle;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isCurrentUser
            ? AppTheme.primaryGreen.withOpacity(0.1)
            : AppTheme.backgroundLight,
        borderRadius: BorderRadius.circular(15),
        border: isCurrentUser
            ? Border.all(color: AppTheme.primaryGreen, width: 2)
            : null,
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: rankColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  rankIcon,
                  color: rankColor,
                  size: 20,
                ),
                Text(
                  '#$rank',
                  style: TextStyle(
                    color: rankColor,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      name,
                      style: TextStyle(
                        color: AppTheme.textDark,
                        fontSize: 15,
                        fontWeight: isCurrentUser ? FontWeight.bold : FontWeight.w600,
                      ),
                    ),
                    if (isCurrentUser) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryGreen,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Text(
                          'أنت',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(MdiIcons.cartOutline, size: 14, color: AppTheme.textLight),
                    const SizedBox(width: 4),
                    Text(
                      NumberFormat.compact().format(sales),
                      style: const TextStyle(
                        color: AppTheme.textLight,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Icon(MdiIcons.cashCheck, size: 14, color: AppTheme.textLight),
                    const SizedBox(width: 4),
                    Text(
                      NumberFormat.compact().format(collections),
                      style: const TextStyle(
                        color: AppTheme.textLight,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShimmer() {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: Container(
        height: 400,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}
