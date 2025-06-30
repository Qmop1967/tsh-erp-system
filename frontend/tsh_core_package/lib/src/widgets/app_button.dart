import 'package:flutter/material.dart';
import '../utils/app_colors.dart';

class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final AppButtonType type;
  final AppButtonSize size;
  final bool isLoading;
  final Widget? icon;
  final bool fullWidth;
  final Color? customColor;
  final Color? customTextColor;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.type = AppButtonType.primary,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
    this.customColor,
    this.customTextColor,
  });

  const AppButton.primary({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
    this.customColor,
    this.customTextColor,
  }) : type = AppButtonType.primary;

  const AppButton.secondary({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
    this.customColor,
    this.customTextColor,
  }) : type = AppButtonType.secondary;

  const AppButton.outline({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
    this.customColor,
    this.customTextColor,
  }) : type = AppButtonType.outline;

  const AppButton.text({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
    this.customColor,
    this.customTextColor,
  }) : type = AppButtonType.text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEnabled = onPressed != null && !isLoading;

    final buttonStyle = _getButtonStyle(theme);
    final textStyle = _getTextStyle(theme);

    Widget child = _buildChild(theme);

    if (fullWidth) {
      child = SizedBox(
        width: double.infinity,
        child: child,
      );
    }

    return child;
  }

  Widget _buildChild(ThemeData theme) {
    if (isLoading) {
      return _buildLoadingButton(theme);
    }

    switch (type) {
      case AppButtonType.primary:
        return ElevatedButton(
          onPressed: onPressed,
          style: _getButtonStyle(theme),
          child: _buildButtonContent(),
        );
      case AppButtonType.secondary:
        return ElevatedButton(
          onPressed: onPressed,
          style: _getButtonStyle(theme),
          child: _buildButtonContent(),
        );
      case AppButtonType.outline:
        return OutlinedButton(
          onPressed: onPressed,
          style: _getButtonStyle(theme),
          child: _buildButtonContent(),
        );
      case AppButtonType.text:
        return TextButton(
          onPressed: onPressed,
          style: _getButtonStyle(theme),
          child: _buildButtonContent(),
        );
    }
  }

  Widget _buildButtonContent() {
    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          icon!,
          const SizedBox(width: 8),
          Text(text),
        ],
      );
    }
    return Text(text);
  }

  Widget _buildLoadingButton(ThemeData theme) {
    return ElevatedButton(
      onPressed: null,
      style: _getButtonStyle(theme).copyWith(
        backgroundColor: WidgetStateProperty.all(
          customColor ?? _getBackgroundColor(theme),
        ),
      ),
      child: SizedBox(
        height: _getIconSize(),
        width: _getIconSize(),
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(
            customTextColor ?? _getTextColor(theme),
          ),
        ),
      ),
    );
  }

  ButtonStyle _getButtonStyle(ThemeData theme) {
    return ButtonStyle(
      padding: WidgetStateProperty.all(_getPadding()),
      minimumSize: WidgetStateProperty.all(_getMinimumSize()),
      shape: WidgetStateProperty.all(
        RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      backgroundColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.disabled)) {
          return AppColors.gray300;
        }
        return customColor ?? _getBackgroundColor(theme);
      }),
      foregroundColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.disabled)) {
          return AppColors.gray500;
        }
        return customTextColor ?? _getTextColor(theme);
      }),
      side: type == AppButtonType.outline
          ? WidgetStateProperty.all(
              BorderSide(
                color: customColor ?? AppColors.primary,
                width: 1,
              ),
            )
          : null,
    );
  }

  TextStyle _getTextStyle(ThemeData theme) {
    final baseStyle = theme.textTheme.labelLarge!;
    switch (size) {
      case AppButtonSize.small:
        return baseStyle.copyWith(fontSize: 12);
      case AppButtonSize.medium:
        return baseStyle.copyWith(fontSize: 14);
      case AppButtonSize.large:
        return baseStyle.copyWith(fontSize: 16);
    }
  }

  Color _getBackgroundColor(ThemeData theme) {
    switch (type) {
      case AppButtonType.primary:
        return AppColors.primary;
      case AppButtonType.secondary:
        return AppColors.secondary;
      case AppButtonType.outline:
        return Colors.transparent;
      case AppButtonType.text:
        return Colors.transparent;
    }
  }

  Color _getTextColor(ThemeData theme) {
    switch (type) {
      case AppButtonType.primary:
        return Colors.white;
      case AppButtonType.secondary:
        return Colors.white;
      case AppButtonType.outline:
        return AppColors.primary;
      case AppButtonType.text:
        return AppColors.primary;
    }
  }

  EdgeInsets _getPadding() {
    switch (size) {
      case AppButtonSize.small:
        return const EdgeInsets.symmetric(horizontal: 12, vertical: 8);
      case AppButtonSize.medium:
        return const EdgeInsets.symmetric(horizontal: 16, vertical: 12);
      case AppButtonSize.large:
        return const EdgeInsets.symmetric(horizontal: 20, vertical: 16);
    }
  }

  Size _getMinimumSize() {
    switch (size) {
      case AppButtonSize.small:
        return const Size(0, 32);
      case AppButtonSize.medium:
        return const Size(0, 40);
      case AppButtonSize.large:
        return const Size(0, 48);
    }
  }

  double _getIconSize() {
    switch (size) {
      case AppButtonSize.small:
        return 16;
      case AppButtonSize.medium:
        return 18;
      case AppButtonSize.large:
        return 20;
    }
  }
}

enum AppButtonType {
  primary,
  secondary,
  outline,
  text,
}

enum AppButtonSize {
  small,
  medium,
  large,
}
