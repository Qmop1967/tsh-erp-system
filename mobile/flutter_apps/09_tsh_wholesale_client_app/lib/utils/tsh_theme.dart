import 'package:flutter/material.dart';

/// TSH Theme - Modern Consumer App
class TSHTheme {
  // Primary Colors - Matching Next.js design (oklch values converted to RGB)
  // --primary: oklch(0.55 0.22 262) -> Purple/Blue
  static const Color primary = Color(0xFF6366F1); // Indigo/Purple
  static const Color primaryForeground = Color(0xFFFFFFFF);

  // --accent: oklch(0.70 0.20 200) -> Cyan/Blue
  static const Color accent = Color(0xFF06B6D4); // Cyan
  static const Color accentForeground = Color(0xFFFFFFFF);

  // Status Colors
  static const Color successGreen = Color(0xFF10B981); // Emerald green
  static const Color success = Color(0xFF10B981); // Alias for successGreen
  static const Color warningOrange = Color(0xFFF59E0B); // Amber
  static const Color errorRed = Color(0xFFEF4444); // Red
  static const Color destructive = Color(0xFFEF4444); // Alias for errorRed

  // Legacy colors for backward compatibility
  static const Color primaryTeal = Color(0xFF06B6D4);
  static const Color primaryBlue = Color(0xFF6366F1);
  static const Color accentOrange = Color(0xFFF59E0B);

  // Surface Colors - Matching Next.js light/dark modes
  static const Color background = Color(0xFFFFFFFF);
  static const Color backgroundLight = Color(0xFFF8FAFC); // Slate 50
  static const Color foreground = Color(0xFF0F172A); // Slate 900
  static const Color card = Color(0xFFFFFFFF);
  static const Color cardForeground = Color(0xFF0F172A);
  static const Color muted = Color(0xFFF1F5F9); // Slate 100
  static const Color mutedForeground = Color(0xFF64748B); // Slate 500
  static const Color border = Color(0xFFE2E8F0); // Slate 200

  // Dark mode colors
  static const Color backgroundDark = Color(0xFF0F172A); // Slate 900
  static const Color foregroundDark = Color(0xFFF8FAFC); // Slate 50
  static const Color cardDark = Color(0xFF1E293B); // Slate 800
  static const Color borderDark = Color(0xFF334155); // Slate 700

  // Legacy colors
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color surfaceLight = Color(0xFFF8F9FA);
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textLight = Color(0xFF94A3B8);

  // Gradient Colors - Matching Next.js design
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, accent],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentGradient = LinearGradient(
    colors: [Color(0xFF06B6D4), Color(0xFF3B82F6)], // Cyan to Blue
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

  // Light Theme - Matching Next.js design system
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: const ColorScheme.light(
      primary: primary,
      onPrimary: primaryForeground,
      secondary: accent,
      onSecondary: accentForeground,
      error: errorRed,
      surface: card,
      onSurface: foreground,
    ),
    scaffoldBackgroundColor: background,
    cardTheme: CardThemeData(
      color: card,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: border, width: 1),
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: primary,
      foregroundColor: primaryForeground,
      elevation: 0,
      centerTitle: false,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: primaryForeground,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primary, width: 2),
      ),
    ),
  );

  // Dark Theme - Matching Next.js dark mode
  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      onPrimary: primaryForeground,
      secondary: accent,
      onSecondary: accentForeground,
      error: errorRed,
      surface: cardDark,
      onSurface: foregroundDark,
    ),
    scaffoldBackgroundColor: backgroundDark,
    cardTheme: CardThemeData(
      color: cardDark,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: borderDark, width: 1),
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: cardDark,
      foregroundColor: foregroundDark,
      elevation: 0,
      centerTitle: false,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: primaryForeground,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: borderDark),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: borderDark),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primary, width: 2),
      ),
    ),
  );

  // Add missing color alias
  static const Color warningYellow = warningOrange;

  // Quick Action Button widget
  static Widget quickActionButton({
    required String label,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: primary.withOpacity(0.2)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: primary, size: 32),
            const SizedBox(height: 8),
            Text(
              label,
              style: bodySmall.copyWith(
                color: textPrimary,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  // Metric Card widget
  static Widget metricCard({
    required String title,
    required String value,
    required IconData icon,
    Color? iconColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: iconColor ?? primary, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: bodySmall.copyWith(color: textSecondary),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: headingMedium.copyWith(color: textPrimary),
          ),
        ],
      ),
    );
  }
}
