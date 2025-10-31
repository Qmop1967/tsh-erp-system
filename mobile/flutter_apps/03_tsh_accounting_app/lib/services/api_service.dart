import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import '../models/dashboard_stats.dart';
import '../models/chart_of_accounts.dart';
import '../models/journal_entry.dart';

/// API Service
/// خدمة الاتصال بـ API النظام المركزي

class ApiService {
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String? _token;
  int? _userId;

  // Initialize with stored credentials
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(AppConfig.tokenKey);
    _userId = prefs.getInt(AppConfig.userIdKey);
  }

  // Get Authorization Headers
  Future<Map<String, String>> _getHeaders() async {
    if (_token == null) {
      await init();
    }

    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (_token != null) 'Authorization': 'Bearer $_token',
    };
  }

  // Login - Authentication
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http
          .post(
            Uri.parse(AppConfig.authUrl),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'email': email,
              'password': password,
            }),
          )
          .timeout(
            Duration(milliseconds: AppConfig.connectionTimeout),
          );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Save credentials
        final prefs = await SharedPreferences.getInstance();
        _token = data['access_token'];
        await prefs.setString(AppConfig.tokenKey, _token!);

        if (data.containsKey('user_id')) {
          _userId = data['user_id'];
          await prefs.setInt(AppConfig.userIdKey, _userId!);
        }

        if (data.containsKey('email')) {
          await prefs.setString(AppConfig.userEmailKey, data['email']);
        }

        if (data.containsKey('role')) {
          await prefs.setString(AppConfig.userRoleKey, data['role']);
        }

        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'message': 'فشل تسجيل الدخول. يرجى التحقق من البيانات.'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'خطأ في الاتصال بالنظام المركزي: ${e.toString()}'
      };
    }
  }

  // Logout
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConfig.tokenKey);
    await prefs.remove(AppConfig.userIdKey);
    _token = null;
    _userId = null;
  }

  // Check if user is authenticated
  Future<bool> isAuthenticated() async {
    if (_token == null) {
      await init();
    }
    return _token != null;
  }

  // ====================
  // DASHBOARD ENDPOINTS
  // ====================

  Future<DashboardStats?> getDashboardStats() async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse(AppConfig.dashboardUrl),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return DashboardStats.fromJson(data);
      }
      return null;
    } catch (e) {
      print('Error fetching dashboard stats: $e');
      return null;
    }
  }

  // ====================
  // CHART OF ACCOUNTS ENDPOINTS
  // ====================

  Future<List<ChartOfAccounts>> getChartOfAccounts() async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse(AppConfig.chartOfAccountsUrl),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((item) => ChartOfAccounts.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      print('Error fetching chart of accounts: $e');
      return [];
    }
  }

  Future<ChartOfAccounts?> getChartOfAccount(int id) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${AppConfig.chartOfAccountsUrl}/$id'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ChartOfAccounts.fromJson(data);
      }
      return null;
    } catch (e) {
      print('Error fetching chart of account: $e');
      return null;
    }
  }

  Future<ChartOfAccounts?> createChartOfAccount(
      ChartOfAccounts account) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .post(
            Uri.parse(AppConfig.chartOfAccountsUrl),
            headers: headers,
            body: json.encode(account.toJson()),
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        return ChartOfAccounts.fromJson(data);
      }
      return null;
    } catch (e) {
      print('Error creating chart of account: $e');
      return null;
    }
  }

  // ====================
  // JOURNAL ENTRIES ENDPOINTS
  // ====================

  Future<List<JournalEntry>> getJournalEntries({
    int? journalId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final headers = await _getHeaders();
      String url = AppConfig.journalEntriesUrl;

      // Add query parameters
      List<String> params = [];
      if (journalId != null) params.add('journal_id=$journalId');
      if (startDate != null) {
        params.add('start_date=${startDate.toIso8601String()}');
      }
      if (endDate != null) {
        params.add('end_date=${endDate.toIso8601String()}');
      }

      if (params.isNotEmpty) {
        url += '?${params.join('&')}';
      }

      final response = await http
          .get(
            Uri.parse(url),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((item) => JournalEntry.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      print('Error fetching journal entries: $e');
      return [];
    }
  }

  Future<JournalEntry?> getJournalEntry(int id) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${AppConfig.journalEntriesUrl}/$id'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return JournalEntry.fromJson(data);
      }
      return null;
    } catch (e) {
      print('Error fetching journal entry: $e');
      return null;
    }
  }

  Future<JournalEntry?> createJournalEntry(JournalEntry entry) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .post(
            Uri.parse(AppConfig.journalEntriesUrl),
            headers: headers,
            body: json.encode(entry.toJson()),
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        return JournalEntry.fromJson(data);
      }
      return null;
    } catch (e) {
      print('Error creating journal entry: $e');
      return null;
    }
  }

  Future<bool> postJournalEntry(int entryId) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .post(
            Uri.parse('${AppConfig.journalEntriesUrl}/$entryId/post'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      return response.statusCode == 200;
    } catch (e) {
      print('Error posting journal entry: $e');
      return false;
    }
  }

  // ====================
  // CURRENCIES ENDPOINTS
  // ====================

  Future<List<Currency>> getCurrencies() async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse(AppConfig.currenciesUrl),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((item) => Currency.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      print('Error fetching currencies: $e');
      return [];
    }
  }

  // ====================
  // REPORTS ENDPOINTS
  // ====================

  Future<Map<String, dynamic>?> getTrialBalance(int periodId) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${AppConfig.trialBalanceUrl}?period_id=$periodId'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error fetching trial balance: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getBalanceSheet(int periodId) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${AppConfig.balanceSheetUrl}?period_id=$periodId'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error fetching balance sheet: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getIncomeStatement(int periodId) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${AppConfig.incomeStatementUrl}?period_id=$periodId'),
            headers: headers,
          )
          .timeout(Duration(milliseconds: AppConfig.connectionTimeout));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error fetching income statement: $e');
      return null;
    }
  }
}
