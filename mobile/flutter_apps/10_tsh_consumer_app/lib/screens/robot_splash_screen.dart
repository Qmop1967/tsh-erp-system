import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../utils/tsh_theme.dart';

/// Animated robot splash screen with development notice
class RobotSplashScreen extends StatefulWidget {
  final VoidCallback onComplete;

  const RobotSplashScreen({
    super.key,
    required this.onComplete,
  });

  @override
  State<RobotSplashScreen> createState() => _RobotSplashScreenState();
}

class _RobotSplashScreenState extends State<RobotSplashScreen>
    with TickerProviderStateMixin {
  late AnimationController _robotController;
  late AnimationController _bounceController;
  late AnimationController _rotateController;
  late AnimationController _fadeController;

  late Animation<double> _bounceAnimation;
  late Animation<double> _rotateAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  bool _showDevelopmentNotice = false;

  @override
  void initState() {
    super.initState();

    // Main robot animation controller
    _robotController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Bounce animation
    _bounceController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _bounceAnimation = Tween<double>(begin: 0, end: -30).animate(
      CurvedAnimation(
        parent: _bounceController,
        curve: Curves.easeInOut,
      ),
    );

    // Rotate animation
    _rotateController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _rotateAnimation = Tween<double>(begin: 0, end: math.pi * 2).animate(
      CurvedAnimation(
        parent: _rotateController,
        curve: Curves.easeInOut,
      ),
    );

    // Scale animation
    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(
        parent: _robotController,
        curve: const Interval(0, 0.5, curve: Curves.elasticOut),
      ),
    );

    // Fade animation for development notice
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _fadeController,
        curve: Curves.easeIn,
      ),
    );

    _startAnimation();
  }

  void _startAnimation() async {
    // Start robot entrance
    await _robotController.forward();

    // Bounce 3 times
    for (int i = 0; i < 3; i++) {
      await _bounceController.forward();
      await _bounceController.reverse();
      await Future.delayed(const Duration(milliseconds: 100));
    }

    // Spin around
    await _rotateController.forward();
    await Future.delayed(const Duration(milliseconds: 300));

    // One more bounce
    await _bounceController.forward();
    await _bounceController.reverse();

    // Show development notice
    setState(() => _showDevelopmentNotice = true);
    await _fadeController.forward();

    // Wait a bit then complete
    await Future.delayed(const Duration(seconds: 2));

    if (mounted) {
      widget.onComplete();
    }
  }

  @override
  void dispose() {
    _robotController.dispose();
    _bounceController.dispose();
    _rotateController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              TSHTheme.primary.withOpacity(0.1),
              TSHTheme.accent.withOpacity(0.1),
              Colors.white,
            ],
          ),
        ),
        child: Stack(
          children: [
            // Animated robot
            Center(
              child: AnimatedBuilder(
                animation: Listenable.merge([
                  _robotController,
                  _bounceController,
                  _rotateController,
                ]),
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(0, _bounceAnimation.value),
                    child: Transform.rotate(
                      angle: _rotateAnimation.value,
                      child: Transform.scale(
                        scale: _scaleAnimation.value,
                        child: _buildRobot(),
                      ),
                    ),
                  );
                },
              ),
            ),

            // Development notice
            if (_showDevelopmentNotice)
              FadeTransition(
                opacity: _fadeAnimation,
                child: Align(
                  alignment: Alignment.bottomCenter,
                  child: Container(
                    margin: const EdgeInsets.all(32),
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: TSHTheme.primary.withOpacity(0.2),
                          blurRadius: 20,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                TSHTheme.primary.withOpacity(0.1),
                                TSHTheme.accent.withOpacity(0.1),
                              ],
                            ),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.construction_rounded,
                            size: 48,
                            color: TSHTheme.primary,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'المتجر قيد التطوير',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            color: TSHTheme.textPrimary,
                            letterSpacing: -0.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'نعمل على تقديم أفضل تجربة تسوق لك',
                          style: TextStyle(
                            fontSize: 16,
                            color: TSHTheme.textSecondary,
                            height: 1.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                TSHTheme.primary.withOpacity(0.1),
                                TSHTheme.accent.withOpacity(0.1),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '🚀 قريباً ميزات جديدة',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: TSHTheme.primary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildRobot() {
    return SizedBox(
      width: 200,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Robot body
          Container(
            width: 120,
            height: 140,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  TSHTheme.primary,
                  TSHTheme.accent,
                ],
              ),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: TSHTheme.primary.withOpacity(0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 20),
                // Eyes
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildEye(),
                    _buildEye(),
                  ],
                ),
                const SizedBox(height: 15),
                // Smile
                Container(
                  width: 50,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ],
            ),
          ),

          // Antenna
          Positioned(
            top: 0,
            child: Container(
              width: 4,
              height: 30,
              decoration: BoxDecoration(
                color: TSHTheme.primary,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Antenna ball
          Positioned(
            top: -5,
            child: Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                color: TSHTheme.accent,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: TSHTheme.accent.withOpacity(0.5),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
            ),
          ),

          // Arms
          Positioned(
            left: 0,
            top: 60,
            child: _buildArm(),
          ),
          Positioned(
            right: 0,
            top: 60,
            child: Transform.scale(
              scaleX: -1,
              child: _buildArm(),
            ),
          ),

          // Legs
          Positioned(
            bottom: 0,
            left: 35,
            child: _buildLeg(),
          ),
          Positioned(
            bottom: 0,
            right: 35,
            child: _buildLeg(),
          ),
        ],
      ),
    );
  }

  Widget _buildEye() {
    return Container(
      width: 20,
      height: 20,
      decoration: const BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: TSHTheme.primary,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }

  Widget _buildArm() {
    return Container(
      width: 40,
      height: 8,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            TSHTheme.primary.withOpacity(0.8),
            TSHTheme.accent.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }

  Widget _buildLeg() {
    return Container(
      width: 20,
      height: 35,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            TSHTheme.primary.withOpacity(0.8),
            TSHTheme.accent.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(10),
      ),
    );
  }
}
