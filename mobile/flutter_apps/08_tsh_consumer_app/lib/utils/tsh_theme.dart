import 'package:flutter/material.dart';

/// TSH Theme - Modern Consumer App
class TSHTheme {
  // Modern Primary Colors
  static const Color primaryTeal = Color(0xFF00BCD4); // Brighter cyan
  static const Color primaryDark = Color(0xFF0097A7); // Dark cyan
  static const Color primaryBlue = Color(0xFF2962FF); // Vibrant blue
  static const Color primaryGold = Color(0xFFFFC107); // Amber gold
  static const Color accentPurple = Color(0xFF7C4DFF); // Modern purple

  // Status Colors
  static const Color successGreen = Color(0xFF00E676); // Bright green
  static const Color warningOrange = Color(0xFFFF6F00); // Deep orange
  static const Color errorRed = Color(0xFFE53935); // Modern red
  static const Color accentOrange = Color(0xFFFF6D00);

  // Surface Colors - Modern Material Design
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color surfaceLight = Color(0xFFF8F9FA);
  static const Color surfaceGrey = Color(0xFFEEEEEE);
  static const Color cardBackground = Color(0xFFFFFFFF);

  // Text Colors
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF666666);
  static const Color textLight = Color(0xFF999999);

  // Gradient Colors
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF00BCD4), Color(0xFF2962FF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFFFC107), Color(0xFFFF6F00)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Text Styles
  static const TextStyle headingLarge = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: textPrimary,
  );

  static const TextStyle headingMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: textPrimary,
  );

  static const TextStyle headingSmall = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.bold,
    color: textPrimary,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    color: textPrimary,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    color: textPrimary,
  );

  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    color: textSecondary,
  );

  // Logo widget
  static Widget tshLogo({double height = 40}) {
    return Icon(
      Icons.store,
      size: height,
      color: surfaceWhite,
    );
  }

  // Light Theme
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryTeal,
      brightness: Brightness.light,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryTeal,
      foregroundColor: Colors.white,
      elevation: 2,
    ),
  );

  // Dark Theme
  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryTeal,
      brightness: Brightness.dark,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.grey[900],
      foregroundColor: Colors.white,
      elevation: 2,
    ),
  );
}
