import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for managing both secure and non-secure storage
class StorageService {
  final FlutterSecureStorage _secureStorage;
  SharedPreferences? _preferences;

  StorageService() : _secureStorage = const FlutterSecureStorage();

  /// Initialize shared preferences
  Future<void> init() async {
    _preferences = await SharedPreferences.getInstance();
  }

  // ========== Secure Storage (for tokens and sensitive data) ==========

  /// Save data securely (encrypted)
  Future<void> saveSecure(String key, String value) async {
    await _secureStorage.write(key: key, value: value);
  }

  /// Read secure data
  Future<String?> readSecure(String key) async {
    return await _secureStorage.read(key: key);
  }

  /// Delete secure data
  Future<void> deleteSecure(String key) async {
    await _secureStorage.delete(key: key);
  }

  /// Clear all secure storage
  Future<void> clearAllSecure() async {
    await _secureStorage.deleteAll();
  }

  // ========== Shared Preferences (for non-sensitive data) ==========

  /// Save JSON data
  Future<bool> saveData(String key, Map<String, dynamic> data) async {
    if (_preferences == null) await init();
    final jsonString = jsonEncode(data);
    return await _preferences!.setString(key, jsonString);
  }

  /// Read JSON data
  Future<Map<String, dynamic>?> getData(String key) async {
    if (_preferences == null) await init();
    final jsonString = _preferences!.getString(key);
    if (jsonString == null) return null;
    try {
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// Remove data
  Future<bool> removeData(String key) async {
    if (_preferences == null) await init();
    return await _preferences!.remove(key);
  }

  /// Save string
  Future<bool> saveString(String key, String value) async {
    if (_preferences == null) await init();
    return await _preferences!.setString(key, value);
  }

  /// Read string
  Future<String?> readString(String key) async {
    if (_preferences == null) await init();
    return _preferences!.getString(key);
  }

  /// Save boolean
  Future<bool> saveBool(String key, bool value) async {
    if (_preferences == null) await init();
    return await _preferences!.setBool(key, value);
  }

  /// Read boolean
  Future<bool?> readBool(String key) async {
    if (_preferences == null) await init();
    return _preferences!.getBool(key);
  }

  /// Save int
  Future<bool> saveInt(String key, int value) async {
    if (_preferences == null) await init();
    return await _preferences!.setInt(key, value);
  }

  /// Read int
  Future<int?> readInt(String key) async {
    if (_preferences == null) await init();
    return _preferences!.getInt(key);
  }

  /// Clear all non-secure storage
  Future<bool> clearAll() async {
    if (_preferences == null) await init();
    return await _preferences!.clear();
  }

  /// Clear everything (both secure and non-secure)
  Future<void> clearEverything() async {
    await clearAllSecure();
    await clearAll();
  }
}
