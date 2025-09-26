import 'package:flutter/material.dart';
import '../utils/app_colors.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final double? elevation;
  final Color? color;
  final double? borderRadius;
  final Border? border;
  final VoidCallback? onTap;
  final bool showShadow;

  const AppCard({
    super.key,
    required this.child,
    this.margin,
    this.padding,
    this.elevation,
    this.color,
    this.borderRadius,
    this.border,
    this.onTap,
    this.showShadow = true,
  });

  const AppCard.flat({
    super.key,
    required this.child,
    this.margin,
    this.padding,
    this.color,
    this.borderRadius,
    this.border,
    this.onTap,
  })  : elevation = 0,
        showShadow = false;

  @override
  Widget build(BuildContext context) {
    Widget card = Container(
      margin: margin,
      decoration: BoxDecoration(
        color: color ?? Colors.white,
        borderRadius: BorderRadius.circular(borderRadius ?? 12),
        border: border,
        boxShadow: showShadow
            ? [
                BoxShadow(
                  color: AppColors.gray900.withValues(alpha: 0.08),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ]
            : null,
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius ?? 12),
        child: Material(
          color: Colors.transparent,
          child: onTap != null
              ? InkWell(
                  onTap: onTap,
                  child: _buildContent(),
                )
              : _buildContent(),
        ),
      ),
    );

    return card;
  }

  Widget _buildContent() {
    return Padding(
      padding: padding ?? const EdgeInsets.all(16),
      child: child,
    );
  }
}

class AppLoadingCard extends StatelessWidget {
  final double? height;
  final EdgeInsets? margin;
  final double? borderRadius;

  const AppLoadingCard({
    super.key,
    this.height,
    this.margin,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      margin: margin,
      borderRadius: borderRadius,
      child: Container(
        height: height ?? 100,
        width: double.infinity,
        decoration: BoxDecoration(
          color: AppColors.gray200,
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      ),
    );
  }
}

class AppInfoCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? icon;
  final Color? backgroundColor;
  final Color? textColor;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final VoidCallback? onTap;
  final InfoCardType type;

  const AppInfoCard({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.backgroundColor,
    this.textColor,
    this.margin,
    this.padding,
    this.onTap,
    this.type = InfoCardType.info,
  });

  const AppInfoCard.success({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.margin,
    this.padding,
    this.onTap,
  })  : backgroundColor = null,
        textColor = null,
        type = InfoCardType.success;

  const AppInfoCard.warning({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.margin,
    this.padding,
    this.onTap,
  })  : backgroundColor = null,
        textColor = null,
        type = InfoCardType.warning;

  const AppInfoCard.error({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.margin,
    this.padding,
    this.onTap,
  })  : backgroundColor = null,
        textColor = null,
        type = InfoCardType.error;

  @override
  Widget build(BuildContext context) {
    final colors = _getColors();
    
    return AppCard(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(16),
      color: backgroundColor ?? colors.backgroundColor,
      onTap: onTap,
      child: Row(
        children: [
          if (icon != null || _getDefaultIcon() != null) ...[
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: colors.iconBackgroundColor,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                _getDefaultIcon(),
                color: colors.iconColor,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: textColor ?? colors.textColor,
                        fontWeight: FontWeight.w600,
                      ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: textColor ?? colors.subtitleColor,
                        ),
                  ),
                ],
              ],
            ),
          ),
          if (onTap != null) ...[
            Icon(
              Icons.chevron_right,
              color: colors.iconColor,
              size: 20,
            ),
          ],
        ],
      ),
    );
  }

  IconData? _getDefaultIcon() {
    switch (type) {
      case InfoCardType.success:
        return Icons.check_circle_outline;
      case InfoCardType.warning:
        return Icons.warning_outlined;
      case InfoCardType.error:
        return Icons.error_outline;
      case InfoCardType.info:
        return Icons.info_outline;
    }
  }

  _InfoCardColors _getColors() {
    switch (type) {
      case InfoCardType.success:
        return _InfoCardColors(
          backgroundColor: AppColors.success.withValues(alpha: 0.1),
          textColor: AppColors.success,
          subtitleColor: AppColors.success.withValues(alpha: 0.8),
          iconColor: AppColors.success,
          iconBackgroundColor: AppColors.success.withValues(alpha: 0.2),
        );
      case InfoCardType.warning:
        return _InfoCardColors(
          backgroundColor: AppColors.warning.withValues(alpha: 0.1),
          textColor: AppColors.warning,
          subtitleColor: AppColors.warning.withValues(alpha: 0.8),
          iconColor: AppColors.warning,
          iconBackgroundColor: AppColors.warning.withValues(alpha: 0.2),
        );
      case InfoCardType.error:
        return _InfoCardColors(
          backgroundColor: AppColors.error.withValues(alpha: 0.1),
          textColor: AppColors.error,
          subtitleColor: AppColors.error.withValues(alpha: 0.8),
          iconColor: AppColors.error,
          iconBackgroundColor: AppColors.error.withValues(alpha: 0.2),
        );
      case InfoCardType.info:
        return _InfoCardColors(
          backgroundColor: AppColors.info.withValues(alpha: 0.1),
          textColor: AppColors.info,
          subtitleColor: AppColors.info.withValues(alpha: 0.8),
          iconColor: AppColors.info,
          iconBackgroundColor: AppColors.info.withValues(alpha: 0.2),
        );
    }
  }
}

class _InfoCardColors {
  final Color backgroundColor;
  final Color textColor;
  final Color subtitleColor;
  final Color iconColor;
  final Color iconBackgroundColor;

  const _InfoCardColors({
    required this.backgroundColor,
    required this.textColor,
    required this.subtitleColor,
    required this.iconColor,
    required this.iconBackgroundColor,
  });
}

enum InfoCardType {
  info,
  success,
  warning,
  error,
}

class AppStatsCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final IconData? icon;
  final Color? color;
  final String? trend;
  final bool isPositiveTrend;
  final VoidCallback? onTap;

  const AppStatsCard({
    super.key,
    required this.title,
    required this.value,
    this.subtitle,
    this.icon,
    this.color,
    this.trend,
    this.isPositiveTrend = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cardColor = color ?? AppColors.primary;

    return AppCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: AppColors.gray600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (icon != null)
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: cardColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: cardColor,
                    size: 20,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.gray900,
            ),
          ),
          if (subtitle != null || trend != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                if (subtitle != null)
                  Expanded(
                    child: Text(
                      subtitle!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: AppColors.gray600,
                      ),
                    ),
                  ),
                if (trend != null) ...[
                  Icon(
                    isPositiveTrend ? Icons.trending_up : Icons.trending_down,
                    size: 16,
                    color: isPositiveTrend ? AppColors.success : AppColors.error,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    trend!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: isPositiveTrend ? AppColors.success : AppColors.error,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ],
            ),
          ],
        ],
      ),
    );
  }
}
