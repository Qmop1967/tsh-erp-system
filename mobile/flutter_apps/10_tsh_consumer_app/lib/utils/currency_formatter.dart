import 'package:intl/intl.dart';

class CurrencyFormatter {
  /// Format amount in IQD currency
  /// Format: 1,500 د.ع (with comma separator, no decimals, Western numerals)
  static String formatIQD(double amount) {
    final formatter = NumberFormat('#,##0', 'en_US');
    final formattedNumber = formatter.format(amount);
    return '$formattedNumber د.ع';
  }

  /// Format amount with custom currency
  static String formatCurrency(double amount, [String currency = 'IQD']) {
    if (currency == 'IQD') {
      return formatIQD(amount);
    }

    try {
      final formatter = NumberFormat.currency(
        locale: 'en_US',
        symbol: currency,
      );
      return formatter.format(amount);
    } catch (e) {
      return '$amount $currency';
    }
  }

  /// Format number with thousand separators
  static String formatNumber(int value) {
    final formatter = NumberFormat('#,##0', 'en_US');
    return formatter.format(value);
  }

  /// Parse currency string to number
  static double parseCurrency(String value) {
    // Remove all non-numeric characters except decimal point
    final cleaned = value.replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(cleaned) ?? 0.0;
  }

  /// Generic format method - delegates to appropriate formatter
  static String format(double amount, [String currency = 'IQD']) {
    return formatCurrency(amount, currency);
  }
}
