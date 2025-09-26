import 'package:flutter/material.dart';

/// TSH ERP System Design System
/// Comprehensive theming and branding for all TSH mobile applications
class TSHTheme {
  // ===============================================
  // BRAND COLORS - Modern Electronics Industry Look
  // ===============================================
  static const Color primaryTeal = Color(0xFF008B8B);
  static const Color primaryBlue = Color(0xFF1E3A8A);
  static const Color accentOrange = Color(0xFFFF6B35);
  static const Color backgroundGrey = Color(0xFFF8FAFC);
  static const Color surfaceWhite = Color(0xFFFFFFFF);
  static const Color textDark = Color(0xFF1F2937);
  static const Color textLight = Color(0xFF6B7280);
  static const Color successGreen = Color(0xFF10B981);
  static const Color warningYellow = Color(0xFFF59E0B);
  static const Color warningOrange = Color(0xFFF97316); // Added missing warningOrange
  static const Color errorRed = Color(0xFFEF4444);
  
  // Text Color Aliases for backward compatibility
  static const Color textPrimary = textDark;
  static const Color textSecondary = textLight;
  
  // Dark Theme Colors
  static const Color darkBackground = Color(0xFF1F2937);
  static const Color darkSurface = Color(0xFF374151);
  static const Color darkTextPrimary = Color(0xFFFFFFFF);
  static const Color darkTextSecondary = Color(0xFFD1D5DB);

  // ===============================================
  // TYPOGRAPHY - Modern, Clean, Readable Fonts
  // ===============================================
  static const String fontFamily = 'Inter'; // Modern, professional font
  
  static const TextStyle headingLarge = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: textDark,
    fontFamily: fontFamily,
  );
  
  static const TextStyle headingMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: textDark,
    fontFamily: fontFamily,
  );
  
  static const TextStyle headingSmall = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: textDark,
    fontFamily: fontFamily,
  );
  
  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: textDark,
    fontFamily: fontFamily,
  );
  
  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: textDark,
    fontFamily: fontFamily,
  );
  
  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: textLight,
    fontFamily: fontFamily,
  );
  
  static const TextStyle buttonText = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    fontFamily: fontFamily,
  );

  // ===============================================
  // LIGHT THEME - Professional Corporate Interface
  // ===============================================
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primaryTeal,
    scaffoldBackgroundColor: backgroundGrey,
    colorScheme: const ColorScheme.light(
      primary: primaryTeal,
      onPrimary: surfaceWhite,
      secondary: accentOrange,
      onSecondary: surfaceWhite,
      surface: surfaceWhite,
      onSurface: textDark,
      background: backgroundGrey,
      onBackground: textDark,
      error: errorRed,
      onError: surfaceWhite,
    ),
    
    // App Bar Theme
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryTeal,
      foregroundColor: surfaceWhite,
      elevation: 2,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: surfaceWhite,
        fontFamily: fontFamily,
      ),
    ),
    
    // Bottom Navigation Theme
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: surfaceWhite,
      selectedItemColor: primaryTeal,
      unselectedItemColor: textLight,
      elevation: 8,
      type: BottomNavigationBarType.fixed,
      selectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
      unselectedLabelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
    ),
    
    // Card Theme
    cardTheme: CardThemeData(
      color: surfaceWhite,
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),
    
    // Elevated Button Theme
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryTeal,
        foregroundColor: surfaceWhite,
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        textStyle: buttonText,
      ),
    ),
    
    // Input Decoration Theme
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: textLight),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryTeal, width: 2),
      ),
      fillColor: surfaceWhite,
      filled: true,
    ),
    
    fontFamily: fontFamily,
  );

  // ===============================================
  // DARK THEME - Professional Dark Mode
  // ===============================================
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primaryTeal,
    scaffoldBackgroundColor: darkBackground,
    colorScheme: const ColorScheme.dark(
      primary: primaryTeal,
      onPrimary: darkBackground,
      secondary: accentOrange,
      onSecondary: darkBackground,
      surface: darkSurface,
      onSurface: darkTextPrimary,
      background: darkBackground,
      onBackground: darkTextPrimary,
      error: errorRed,
      onError: darkBackground,
    ),
    
    appBarTheme: const AppBarTheme(
      backgroundColor: darkSurface,
      foregroundColor: darkTextPrimary,
      elevation: 2,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: darkTextPrimary,
        fontFamily: fontFamily,
      ),
    ),
    
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: darkSurface,
      selectedItemColor: primaryTeal,
      unselectedItemColor: darkTextSecondary,
      elevation: 8,
      type: BottomNavigationBarType.fixed,
    ),
    
    cardTheme: CardThemeData(
      color: darkSurface,
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),
    
    fontFamily: fontFamily,
  );

  // ===============================================
  // LAYOUT CONSTANTS - Spacing and Sizing
  // ===============================================
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  static const double paddingXLarge = 32.0;
  
  static const double radiusSmall = 4.0;
  static const double radiusMedium = 8.0;
  static const double radiusLarge = 12.0;
  static const double radiusXLarge = 16.0;
  
  static const double iconSizeSmall = 20.0;
  static const double iconSizeMedium = 24.0;
  static const double iconSizeLarge = 32.0;
  static const double iconSizeXLarge = 48.0;

  // ===============================================
  // TSH BRAND LOGO WIDGET
  // ===============================================
  static Widget tshLogo({double height = 40}) {
    return Container(
      height: height,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: height,
            height: height,
            decoration: BoxDecoration(
              color: primaryTeal,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: Text(
                'TSH',
                style: TextStyle(
                  color: surfaceWhite,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          const Text(
            'TSH ERP',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: primaryTeal,
            ),
          ),
        ],
      ),
    );
  }

  // ===============================================
  // IRAQI DINAR CURRENCY FORMATTER
  // ===============================================
  static String formatIraqiDinar(double amount) {
    // Format with thousands separator for Iraqi market
    String formatted = amount.toStringAsFixed(0);
    
    // Add thousands separator (Iraqi format)
    List<String> parts = [];
    for (int i = formatted.length; i > 0; i -= 3) {
      int start = i - 3 < 0 ? 0 : i - 3;
      parts.insert(0, formatted.substring(start, i));
    }
    
    return '${parts.join(',')} IQD';
  }

  // ===============================================
  // QUICK ACTION BUTTON WIDGET
  // ===============================================
  static Widget quickActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    Color? backgroundColor,
    Color? iconColor,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(radiusLarge),
      child: Container(
        padding: const EdgeInsets.all(paddingMedium),
        decoration: BoxDecoration(
          color: backgroundColor ?? primaryTeal.withOpacity(0.1),
          borderRadius: BorderRadius.circular(radiusLarge),
          border: Border.all(color: primaryTeal.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: iconSizeLarge,
              color: iconColor ?? primaryTeal,
            ),
            const SizedBox(height: paddingSmall),
            Text(
              label,
              style: bodySmall.copyWith(
                color: iconColor ?? primaryTeal,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  // ===============================================
  // DASHBOARD METRIC CARD WIDGET
  // ===============================================
  static Widget metricCard({
    required String title,
    required String value,
    required IconData icon,
    Color? iconColor,
    String? subtitle,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(paddingMedium),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: iconColor ?? primaryTeal,
                  size: iconSizeLarge,
                ),
                const Spacer(),
                if (subtitle != null)
                  Text(
                    subtitle,
                    style: bodySmall,
                  ),
              ],
            ),
            const SizedBox(height: paddingSmall),
            Text(
              title,
              style: bodyMedium.copyWith(color: textLight),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: headingMedium.copyWith(color: primaryTeal),
            ),
          ],
        ),
      ),
    );
  }
}