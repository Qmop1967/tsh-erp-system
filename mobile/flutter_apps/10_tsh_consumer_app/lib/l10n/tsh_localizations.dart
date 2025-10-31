import 'package:flutter/material.dart';

class TSHLocalizations {
  final Locale locale;

  TSHLocalizations(this.locale);

  static TSHLocalizations? of(BuildContext context) {
    return Localizations.of<TSHLocalizations>(context, TSHLocalizations);
  }

  static const delegate = _TSHLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('en'),
    Locale('ar'),
  ];

  static final Map<String, Map<String, String>> _localizedValues = {
    'en': {
      'tsh_consumer_app': 'TSH Consumer',
      'welcome_message': 'Welcome to TSH Electronics',
      'products': 'Products',
      'orders': 'Orders',
    },
    'ar': {
      'tsh_consumer_app': 'متجر TSH',
      'welcome_message': 'مرحباً بك في TSH للإلكترونيات',
      'products': 'المنتجات',
      'orders': 'الطلبات',
    },
  };

  String translate(String key) {
    return _localizedValues[locale.languageCode]?[key] ?? key;
  }
}

class _TSHLocalizationsDelegate extends LocalizationsDelegate<TSHLocalizations> {
  const _TSHLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ar'].contains(locale.languageCode);
  }

  @override
  Future<TSHLocalizations> load(Locale locale) async {
    return TSHLocalizations(locale);
  }

  @override
  bool shouldReload(_TSHLocalizationsDelegate old) => false;
}
