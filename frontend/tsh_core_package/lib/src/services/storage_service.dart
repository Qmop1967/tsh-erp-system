import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _keyPrefix = 'tsh_erp_';
  
  Future<SharedPreferences> get _prefs async => await SharedPreferences.getInstance();

  // Generic data storage
  Future<void> saveData(String key, Map<String, dynamic> data) async {
    final prefs = await _prefs;
    final jsonString = jsonEncode(data);
    await prefs.setString('$_keyPrefix$key', jsonString);
  }

  Future<Map<String, dynamic>?> getData(String key) async {
    final prefs = await _prefs;
    final jsonString = prefs.getString('$_keyPrefix$key');
    if (jsonString != null) {
      try {
        return jsonDecode(jsonString) as Map<String, dynamic>;
      } catch (e) {
        // If decoding fails, remove the corrupted data
        await removeData(key);
        return null;
      }
    }
    return null;
  }

  Future<void> removeData(String key) async {
    final prefs = await _prefs;
    await prefs.remove('$_keyPrefix$key');
  }

  // String storage
  Future<void> saveString(String key, String value) async {
    final prefs = await _prefs;
    await prefs.setString('$_keyPrefix$key', value);
  }

  Future<String?> getString(String key) async {
    final prefs = await _prefs;
    return prefs.getString('$_keyPrefix$key');
  }

  // Boolean storage
  Future<void> saveBool(String key, bool value) async {
    final prefs = await _prefs;
    await prefs.setBool('$_keyPrefix$key', value);
  }

  Future<bool> getBool(String key, {bool defaultValue = false}) async {
    final prefs = await _prefs;
    return prefs.getBool('$_keyPrefix$key') ?? defaultValue;
  }

  // Integer storage
  Future<void> saveInt(String key, int value) async {
    final prefs = await _prefs;
    await prefs.setInt('$_keyPrefix$key', value);
  }

  Future<int> getInt(String key, {int defaultValue = 0}) async {
    final prefs = await _prefs;
    return prefs.getInt('$_keyPrefix$key') ?? defaultValue;
  }

  // Double storage
  Future<void> saveDouble(String key, double value) async {
    final prefs = await _prefs;
    await prefs.setDouble('$_keyPrefix$key', value);
  }

  Future<double> getDouble(String key, {double defaultValue = 0.0}) async {
    final prefs = await _prefs;
    return prefs.getDouble('$_keyPrefix$key') ?? defaultValue;
  }

  // List storage
  Future<void> saveStringList(String key, List<String> values) async {
    final prefs = await _prefs;
    await prefs.setStringList('$_keyPrefix$key', values);
  }

  Future<List<String>> getStringList(String key) async {
    final prefs = await _prefs;
    return prefs.getStringList('$_keyPrefix$key') ?? [];
  }

  // Cache with expiration
  Future<void> saveWithExpiration(
    String key,
    Map<String, dynamic> data,
    Duration expiration,
  ) async {
    final expirationTime = DateTime.now().add(expiration).millisecondsSinceEpoch;
    final cacheData = {
      'data': data,
      'expiration': expirationTime,
    };
    await saveData('cache_$key', cacheData);
  }

  Future<Map<String, dynamic>?> getWithExpiration(String key) async {
    final cacheData = await getData('cache_$key');
    if (cacheData == null) return null;

    final expiration = cacheData['expiration'] as int?;
    if (expiration == null) return null;

    if (DateTime.now().millisecondsSinceEpoch > expiration) {
      // Cache expired, remove it
      await removeData('cache_$key');
      return null;
    }

    return cacheData['data'] as Map<String, dynamic>?;
  }

  // Clear all app data
  Future<void> clearAll() async {
    final prefs = await _prefs;
    final keys = prefs.getKeys().where((key) => key.startsWith(_keyPrefix));
    for (final key in keys) {
      await prefs.remove(key);
    }
  }

  // Check if key exists
  Future<bool> hasKey(String key) async {
    final prefs = await _prefs;
    return prefs.containsKey('$_keyPrefix$key');
  }

  // Get all keys with prefix
  Future<List<String>> getAllKeys() async {
    final prefs = await _prefs;
    return prefs.getKeys()
        .where((key) => key.startsWith(_keyPrefix))
        .map((key) => key.substring(_keyPrefix.length))
        .toList();
  }
}
