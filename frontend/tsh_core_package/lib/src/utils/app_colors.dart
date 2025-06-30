import 'package:flutter/material.dart';

/// TSH ERP App Colors - ألوان تطبيق TSH ERP
class AppColors {
  // Primary Colors - الألوان الأساسية
  static const Color primary = Color(0xFF1565C0); // Deep Blue
  static const Color primaryLight = Color(0xFF42A5F5); // Light Blue
  static const Color primaryDark = Color(0xFF0D47A1); // Dark Blue
  static const Color secondary = Color(0xFF00ACC1); // Cyan
  static const Color accent = Color(0xFFFF7043); // Deep Orange

  // Background Colors - ألوان الخلفية
  static const Color background = Color(0xFFF5F5F5); // Light Grey
  static const Color surface = Color(0xFFFFFFFF); // White
  static const Color surfaceVariant = Color(0xFFF3F4F6); // Light Grey Variant
  
  // Dark Theme Colors - ألوان الوضع الداكن
  static const Color darkBackground = Color(0xFF121212); // Dark Background
  static const Color darkSurface = Color(0xFF1E1E1E); // Dark Surface

  // Text Colors - ألوان النص
  static const Color textPrimary = Color(0xFF212121); // Dark Grey
  static const Color textSecondary = Color(0xFF757575); // Medium Grey
  static const Color textHint = Color(0xFF9E9E9E); // Light Grey
  static const Color textOnPrimary = Color(0xFFFFFFFF); // White
  
  // Text Secondary Variants - متغيرات ألوان النص الثانوي  
  static const Color textSecondary100 = Color(0xFFF5F5F5);
  static const Color textSecondary300 = Color(0xFFE0E0E0);
  static const Color textSecondary400 = Color(0xFFBDBDBD);
  static const Color textSecondary500 = Color(0xFF9E9E9E);
  static const Color textSecondary700 = Color(0xFF616161);

  // Gray Scale Colors - ألوان الرمادي المتدرج
  static const Color gray50 = Color(0xFFFAFAFA);   // Lightest Gray
  static const Color gray100 = Color(0xFFF5F5F5);  // Very Light Gray
  static const Color gray200 = Color(0xFFEEEEEE);  // Light Gray
  static const Color gray300 = Color(0xFFE0E0E0);  // Medium Light Gray
  static const Color gray400 = Color(0xFFBDBDBD);  // Medium Gray
  static const Color gray500 = Color(0xFF9E9E9E);  // Gray
  static const Color gray600 = Color(0xFF757575);  // Medium Dark Gray
  static const Color gray700 = Color(0xFF616161);  // Dark Gray
  static const Color gray800 = Color(0xFF424242);  // Very Dark Gray
  static const Color gray900 = Color(0xFF212121);  // Darkest Gray

  // Status Colors - ألوان الحالة
  static const Color success = Color(0xFF4CAF50); // Green
  static const Color warning = Color(0xFFFF9800); // Orange
  static const Color error = Color(0xFFE53935); // Red
  static const Color info = Color(0xFF2196F3); // Blue

  // Border Colors - ألوان الحدود
  static const Color border = Color(0xFFE0E0E0); // Light Grey
  static const Color borderFocus = Color(0xFF1976D2); // Blue

  // Shadows - الظلال
  static const Color shadow = Color(0x1A000000); // Black with 10% opacity

  // Gradients - التدرجات
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, primaryLight],
  );

  static const LinearGradient secondaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [secondary, Color(0xFF26C6DA)],
  );

  // App-specific colors - ألوان خاصة بالتطبيق
  static const Color travel = Color(0xFF8E24AA); // Purple
  static const Color retail = Color(0xFF00796B); // Teal
  static const Color client = Color(0xFF5D4037); // Brown
  static const Color consumer = Color(0xFFE65100); // Deep Orange
  static const Color partner = Color(0xFF1976D2); // Blue
  static const Color admin = Color(0xFF424242); // Dark Grey

  // Currency Colors - ألوان العملات
  static const Color iqd = Color(0xFF388E3C); // Green for IQD
  static const Color usd = Color(0xFF1976D2); // Blue for USD
  static const Color rmb = Color(0xFFD32F2F); // Red for RMB

  // Chart Colors - ألوان المخططات
  static const List<Color> chartColors = [
    Color(0xFF1976D2),
    Color(0xFF388E3C),
    Color(0xFFE65100),
    Color(0xFF7B1FA2),
    Color(0xFF00796B),
    Color(0xFFD32F2F),
    Color(0xFF5D4037),
    Color(0xFF424242),
  ];
}
