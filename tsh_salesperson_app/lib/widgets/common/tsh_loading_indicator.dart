import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:shimmer/shimmer.dart';

class TSHLoadingIndicator extends StatelessWidget {
  final String? message;
  final double size;
  final Color? color;
  final bool showMessage;

  const TSHLoadingIndicator({
    super.key,
    this.message,
    this.size = 60.0,
    this.color,
    this.showMessage = true,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Try to use Lottie animation first, fall back to CircularProgressIndicator
          _buildLoadingWidget(context),
          if (showMessage && message != null) ...[
            const SizedBox(height: 16),
            Text(
              message!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: color ?? Theme.of(context).primaryColor,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLoadingWidget(BuildContext context) {
    // Try to load Lottie animation, fallback to CircularProgressIndicator
    try {
      return SizedBox(
        width: size,
        height: size,
        child: Lottie.asset(
          'assets/animations/loading.json',
          width: size,
          height: size,
          errorBuilder: (context, error, stackTrace) {
            return _buildCircularIndicator(context);
          },
        ),
      );
    } catch (e) {
      return _buildCircularIndicator(context);
    }
  }

  Widget _buildCircularIndicator(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(
        strokeWidth: 3.0,
        valueColor: AlwaysStoppedAnimation<Color>(
          color ?? Theme.of(context).primaryColor,
        ),
      ),
    );
  }
}

// Simple loading overlay
class TSHLoadingOverlay extends StatelessWidget {
  final Widget child;
  final bool isLoading;
  final String? loadingMessage;
  final Color? overlayColor;

  const TSHLoadingOverlay({
    super.key,
    required this.child,
    required this.isLoading,
    this.loadingMessage,
    this.overlayColor,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Container(
            color: overlayColor ?? Colors.black.withOpacity(0.5),
            child: TSHLoadingIndicator(
              message: loadingMessage ?? 'Loading...',
              color: Colors.white,
            ),
          ),
      ],
    );
  }
}

// Shimmer loading placeholder
class TSHShimmerLoading extends StatelessWidget {
  final Widget child;
  final bool isLoading;
  final Color? baseColor;
  final Color? highlightColor;

  const TSHShimmerLoading({
    super.key,
    required this.child,
    required this.isLoading,
    this.baseColor,
    this.highlightColor,
  });

  @override
  Widget build(BuildContext context) {
    if (!isLoading) return child;

    return Shimmer.fromColors(
      baseColor: baseColor ?? Colors.grey[300]!,
      highlightColor: highlightColor ?? Colors.grey[100]!,
      child: child,
    );
  }
}

// Skeleton loading for lists
class TSHSkeletonLoader extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  final EdgeInsetsGeometry? padding;

  const TSHSkeletonLoader({
    super.key,
    this.itemCount = 5,
    this.itemHeight = 80.0,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: padding,
      itemCount: itemCount,
      itemBuilder: (context, index) => TSHShimmerLoading(
        isLoading: true,
        child: Container(
          height: itemHeight,
          margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
      ),
    );
  }
}
