import 'package:flutter/material.dart';

class LanguageService extends ChangeNotifier {
  Locale _currentLocale = const Locale('en');
  bool _isDarkMode = false;

  Locale get currentLocale => _currentLocale;
  bool get isDarkMode => _isDarkMode;
  bool get isRTL => _currentLocale.languageCode == 'ar';

  void setLocale(Locale locale) {
    _currentLocale = locale;
    notifyListeners();
  }

  void toggleLanguage() {
    _currentLocale = _currentLocale.languageCode == 'en'
        ? const Locale('ar')
        : const Locale('en');
    notifyListeners();
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
  }
}
