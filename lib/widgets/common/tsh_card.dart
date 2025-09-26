import 'dart:ui';
import 'package:flutter/material.dart';
import '../../config/app_theme.dart';

class TSHCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;
  final double? elevation;
  final BorderRadius? borderRadius;
  final List<BoxShadow>? boxShadow;
  final Gradient? gradient;
  final Border? border;
  final double? width;
  final double? height;
  final bool animate;

  const TSHCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding,
    this.margin,
    this.backgroundColor,
    this.elevation,
    this.borderRadius,
    this.boxShadow,
    this.gradient,
    this.border,
    this.width,
    this.height,
    this.animate = true,
  });

  @override
  State<TSHCard> createState() => _TSHCardState();
}

class _TSHCardState extends State<TSHCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _shadowAnimation;

  @override
  void initState() {
    super.initState();
    
    if (widget.animate) {
      _controller = AnimationController(
        duration: const Duration(milliseconds: 150),
        vsync: this,
      );
      
      _scaleAnimation = Tween<double>(
        begin: 1.0,
        end: 0.98,
      ).animate(CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ));
      
      _shadowAnimation = Tween<double>(
        begin: 1.0,
        end: 0.5,
      ).animate(CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ));
    }
  }

  @override
  void dispose() {
    if (widget.animate) {
      _controller.dispose();
    }
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    if (widget.animate && widget.onTap != null) {
      _controller.forward();
    }
  }

  void _onTapUp(TapUpDetails details) {
    if (widget.animate && widget.onTap != null) {
      _controller.reverse();
    }
  }

  void _onTapCancel() {
    if (widget.animate && widget.onTap != null) {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget cardWidget = Container(
      width: widget.width,
      height: widget.height,
      margin: widget.margin,
      decoration: BoxDecoration(
        color: widget.backgroundColor ?? Colors.white,
        gradient: widget.gradient,
        borderRadius: widget.borderRadius ?? AppTheme.largeRadius,
        border: widget.border,
        boxShadow: widget.boxShadow ?? _getDefaultShadow(),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: widget.borderRadius ?? AppTheme.largeRadius,
        child: InkWell(
          onTap: widget.onTap,
          borderRadius: widget.borderRadius ?? AppTheme.largeRadius,
          splashColor: AppTheme.primaryGreen.withOpacity(0.1),
          highlightColor: AppTheme.primaryGreen.withOpacity(0.05),
          child: Container(
            padding: widget.padding,
            child: widget.child,
          ),
        ),
      ),
    );

    if (widget.animate && widget.onTap != null) {
      return GestureDetector(
        onTapDown: _onTapDown,
        onTapUp: _onTapUp,
        onTapCancel: _onTapCancel,
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: widget.borderRadius ?? AppTheme.largeRadius,
                  boxShadow: (widget.boxShadow ?? _getDefaultShadow())
                      .map((shadow) => BoxShadow(
                            color: shadow.color,
                            blurRadius: shadow.blurRadius * _shadowAnimation.value,
                            offset: shadow.offset,
                            spreadRadius: shadow.spreadRadius,
                          ))
                      .toList(),
                ),
                child: cardWidget,
              ),
            );
          },
        ),
      );
    }

    return cardWidget;
  }

  List<BoxShadow> _getDefaultShadow() {
    return [
      BoxShadow(
        color: Colors.black.withOpacity(0.08),
        blurRadius: 16,
        offset: const Offset(0, 4),
        spreadRadius: 0,
      ),
      BoxShadow(
        color: Colors.black.withOpacity(0.04),
        blurRadius: 8,
        offset: const Offset(0, 2),
        spreadRadius: 0,
      ),
    ];
  }
}

class TSHGlassCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final double opacity;
  final double blur;

  const TSHGlassCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.borderRadius,
    this.opacity = 0.1,
    this.blur = 10.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: margin,
      child: ClipRRect(
        borderRadius: borderRadius ?? AppTheme.largeRadius,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(opacity),
              borderRadius: borderRadius ?? AppTheme.largeRadius,
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onTap,
                borderRadius: borderRadius ?? AppTheme.largeRadius,
                child: Container(
                  padding: padding,
                  child: child,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class TSHElevatedCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final double elevation;

  const TSHElevatedCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding,
    this.margin,
    this.backgroundColor,
    this.width,
    this.height,
    this.borderRadius,
    this.elevation = 8.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: margin,
      child: Material(
        color: backgroundColor ?? Colors.white,
        elevation: elevation,
        borderRadius: borderRadius ?? AppTheme.largeRadius,
        child: InkWell(
          onTap: onTap,
          borderRadius: borderRadius ?? AppTheme.largeRadius,
          child: Container(
            padding: padding,
            child: child,
          ),
        ),
      ),
    );
  }
}

class TSHGradientCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final Gradient gradient;

  const TSHGradientCard({
    super.key,
    required this.child,
    required this.gradient,
    this.onTap,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    return TSHCard(
      onTap: onTap,
      padding: padding,
      margin: margin,
      width: width,
      height: height,
      borderRadius: borderRadius,
      gradient: gradient,
      child: child,
    );
  }
} 