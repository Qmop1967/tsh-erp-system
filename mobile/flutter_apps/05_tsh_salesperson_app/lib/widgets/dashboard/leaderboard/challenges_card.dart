import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:shimmer/shimmer.dart';

import '../../../config/app_theme.dart';

class ChallengesCard extends StatelessWidget {
  final Map<String, dynamic>? leaderboardData;
  final bool isLoading;

  const ChallengesCard({
    super.key,
    this.leaderboardData,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _buildShimmer();
    }

    final challenges = leaderboardData?['challenges'] ?? [];

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
                  MdiIcons.trophy,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'التحديات النشطة',
                style: TextStyle(
                  color: AppTheme.textDark,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (challenges.isEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Icon(
                      MdiIcons.trophyOutline,
                      size: 64,
                      color: AppTheme.textLight.withOpacity(0.5),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'لا توجد تحديات نشطة حالياً',
                      style: TextStyle(
                        color: AppTheme.textLight,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            ...challenges.map((challenge) => _buildChallengeItem(
              title: challenge['title'] ?? 'تحدي',
              description: challenge['description'] ?? '',
              progress: (challenge['progress'] ?? 0.0) as double,
              reward: challenge['reward'] ?? '',
              isCompleted: challenge['is_completed'] ?? false,
            )).toList(),
        ],
      ),
    );
  }

  Widget _buildChallengeItem({
    required String title,
    required String description,
    required double progress,
    required String reward,
    required bool isCompleted,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: isCompleted
            ? AppTheme.goldGradient
            : LinearGradient(
                colors: [
                  AppTheme.backgroundLight,
                  AppTheme.backgroundLight,
                ],
              ),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: isCompleted ? Colors.transparent : Colors.grey[300]!,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isCompleted ? MdiIcons.checkCircle : MdiIcons.target,
                color: isCompleted ? Colors.white : AppTheme.goldAccent,
                size: 24,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        color: isCompleted ? Colors.white : AppTheme.textDark,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: TextStyle(
                        color: isCompleted ? Colors.white70 : AppTheme.textLight,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (isCompleted)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'مكتمل',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: isCompleted
                  ? Colors.white.withOpacity(0.3)
                  : Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                isCompleted ? Colors.white : AppTheme.goldAccent,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${(progress * 100).toStringAsFixed(0)}% مكتمل',
                style: TextStyle(
                  color: isCompleted ? Colors.white70 : AppTheme.textLight,
                  fontSize: 12,
                ),
              ),
              Row(
                children: [
                  Icon(
                    MdiIcons.giftOutline,
                    color: isCompleted ? Colors.white70 : AppTheme.goldAccent,
                    size: 14,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    reward,
                    style: TextStyle(
                      color: isCompleted ? Colors.white : AppTheme.goldAccent,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ],
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
        height: 250,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}
