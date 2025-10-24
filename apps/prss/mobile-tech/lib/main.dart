import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'config/app_config.dart';

void main() {
  runApp(const ASOApp());
}

class ASOApp extends StatelessWidget {
  const ASOApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH ASO',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          elevation: 2,
        ),
      ),
      home: const SplashScreen(),
    );
  }
}

// Splash Screen
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(seconds: 2));
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (!mounted) return;

    if (token != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const HomeScreen()),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(
              Icons.build_circle,
              size: 120,
              color: Colors.white,
            ),
            SizedBox(height: 24),
            Text(
              'TSH ASO',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 2,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'After-Sales Operations',
              style: TextStyle(
                fontSize: 16,
                color: Colors.white70,
              ),
            ),
            SizedBox(height: 48),
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}

// Login Screen
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _error = '';

  Future<void> _login() async {
    // Validate input fields
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();

    // Check if fields are empty
    if (username.isEmpty || password.isEmpty) {
      setState(() {
        _error = 'يرجى إدخال اسم المستخدم وكلمة المرور';
      });
      return;
    }

    // Check minimum length
    if (username.length < 3 || password.length < 6) {
      setState(() {
        _error = 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل وكلمة المرور 6 أحرف';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      // Call central API for authentication
      final response = await http.post(
        Uri.parse(AppConfig.authUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': username,
          'password': password,
        }),
      ).timeout(
        Duration(milliseconds: AppConfig.connectionTimeout),
        onTimeout: () {
          throw Exception('انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى.');
        },
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Save user data to local storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConfig.tokenKey, data['access_token']);
        await prefs.setString(AppConfig.usernameKey, username);

        // Save user ID if provided
        if (data.containsKey('user_id')) {
          await prefs.setInt(AppConfig.userIdKey, data['user_id']);
        }

        // Save user role if provided
        if (data.containsKey('role')) {
          await prefs.setString(AppConfig.userRoleKey, data['role']);
        }

        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen()),
        );
      } else if (response.statusCode == 401) {
        setState(() {
          _isLoading = false;
          _error = 'اسم المستخدم أو كلمة المرور غير صحيحة';
        });
      } else {
        setState(() {
          _isLoading = false;
          _error = 'حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.';
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        if (e.toString().contains('انتهت مهلة الاتصال')) {
          _error = 'انتهت مهلة الاتصال. تأكد من تشغيل النظام المركزي.';
        } else {
          _error = 'خطأ في الاتصال بالنظام المركزي. يرجى التحقق من الاتصال بالإنترنت.';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.build_circle,
                size: 100,
                color: Colors.blue,
              ),
              const SizedBox(height: 24),
              const Text(
                'TSH ASO',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'تسجيل الدخول',
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 48),
              TextField(
                controller: _usernameController,
                decoration: InputDecoration(
                  labelText: 'Username',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: const Icon(Icons.person),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: const Icon(Icons.lock),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          'تسجيل الدخول',
                          style: TextStyle(fontSize: 18),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Home Screen
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _username = '';
  int _notificationCount = 3; // عدد الإشعارات غير المقروءة

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    _loadNotifications();
  }

  Future<void> _loadUserInfo() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _username = prefs.getString('username') ?? 'Technician';
    });
  }

  Future<void> _loadNotifications() async {
    // في الإصدار الكامل، سيتم جلب الإشعارات من الـ API
    // هنا نستخدم بيانات تجريبية
    await Future.delayed(const Duration(milliseconds: 500));
    if (mounted) {
      setState(() {
        _notificationCount = 3;
      });
    }
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TSH ASO'),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => NotificationsScreen(
                        onNotificationsRead: () {
                          setState(() {
                            _notificationCount = 0;
                          });
                        },
                      ),
                    ),
                  );
                },
              ),
              if (_notificationCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 20,
                      minHeight: 20,
                    ),
                    child: Text(
                      '$_notificationCount',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: Colors.blue,
                      child: Text(
                        _username.isNotEmpty ? _username[0].toUpperCase() : 'T',
                        style: const TextStyle(
                          fontSize: 24,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'مرحباً, $_username',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Text(
                          'فني صيانة',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'إحصائيات اليوم',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: const [
                Expanded(
                  child: _StatCard(
                    icon: Icons.pending_actions,
                    title: 'قيد الانتظار',
                    value: '5',
                    color: Colors.orange,
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: _StatCard(
                    icon: Icons.check_circle,
                    title: 'مكتملة',
                    value: '12',
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'القائمة',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _MenuItem(
              icon: Icons.list_alt,
              title: 'مهام الصيانة',
              subtitle: '5 مهام قيد الانتظار',
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const MaintenanceJobsScreen(),
                  ),
                );
              },
            ),
            _MenuItem(
              icon: Icons.qr_code_scanner,
              title: 'مسح السيريال',
              subtitle: 'مسح رمز المنتج',
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const QRScannerScreen(),
                  ),
                );
              },
            ),
            _MenuItem(
              icon: Icons.assignment,
              title: 'طلبات الإرجاع',
              subtitle: 'عرض جميع الطلبات',
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ReturnsListScreen(),
                  ),
                );
              },
            ),
            _MenuItem(
              icon: Icons.history,
              title: 'سجل الأعمال',
              subtitle: 'عرض سجل الصيانة',
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const WorkHistoryScreen(),
                  ),
                );
              },
            ),
            _MenuItem(
              icon: Icons.settings,
              title: 'الإعدادات',
              subtitle: 'إعدادات التطبيق',
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const SettingsScreen(),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

// Stat Card Widget
class _StatCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Menu Item Widget
class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.blue.shade50,
          child: Icon(icon, color: Colors.blue),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}

// Maintenance Jobs Screen
class MaintenanceJobsScreen extends StatelessWidget {
  const MaintenanceJobsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final jobs = [
      {
        'id': 'MNT-001',
        'product': 'لاب توب HP ProBook 450',
        'serial': 'SN-12345',
        'issue': 'الشاشة لا تعمل',
      },
      {
        'id': 'MNT-002',
        'product': 'طابعة HP LaserJet',
        'serial': 'SN-67890',
        'issue': 'لا تطبع',
      },
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('مهام الصيانة'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: jobs.length,
        itemBuilder: (context, index) {
          final job = jobs[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: const CircleAvatar(
                backgroundColor: Colors.blue,
                child: Icon(Icons.build, color: Colors.white),
              ),
              title: Text(
                job['product'] as String,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text('${job['id']} - ${job['serial']}\n${job['issue']}'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('فتح ${job['id']}')),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

// Notifications Screen
class NotificationsScreen extends StatefulWidget {
  final VoidCallback onNotificationsRead;

  const NotificationsScreen({
    super.key,
    required this.onNotificationsRead,
  });

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final List<Map<String, dynamic>> _notifications = [
    {
      'id': 1,
      'title': 'مهمة صيانة جديدة',
      'body': 'تم تعيين مهمة صيانة MNT-001 لك',
      'time': '10 دقائق',
      'icon': Icons.build,
      'color': Colors.blue,
      'read': false,
    },
    {
      'id': 2,
      'title': 'تحديث حالة المنتج',
      'body': 'تم تحديث حالة المنتج SN-12345 إلى "قيد الفحص"',
      'time': 'ساعة واحدة',
      'icon': Icons.info,
      'color': Colors.orange,
      'read': false,
    },
    {
      'id': 3,
      'title': 'موافقة الضمان',
      'body': 'تمت الموافقة على طلب الضمان للمنتج SN-67890',
      'time': '3 ساعات',
      'icon': Icons.check_circle,
      'color': Colors.green,
      'read': false,
    },
    {
      'id': 4,
      'title': 'تذكير',
      'body': 'لديك مهمتان قيد الانتظار تحتاج إلى إكمال',
      'time': 'أمس',
      'icon': Icons.notification_important,
      'color': Colors.red,
      'read': true,
    },
    {
      'id': 5,
      'title': 'إكتمال الصيانة',
      'body': 'تم إكمال صيانة المنتج SN-54321 بنجاح',
      'time': 'يومان',
      'icon': Icons.done_all,
      'color': Colors.teal,
      'read': true,
    },
  ];

  @override
  void initState() {
    super.initState();
    // تحديد الإشعارات كمقروءة بعد فتح الشاشة
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted) {
        widget.onNotificationsRead();
      }
    });
  }

  void _markAsRead(int id) {
    setState(() {
      final notification = _notifications.firstWhere((n) => n['id'] == id);
      notification['read'] = true;
    });
  }

  void _markAllAsRead() {
    setState(() {
      for (var notification in _notifications) {
        notification['read'] = true;
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم تحديد جميع الإشعارات كمقروءة')),
    );
  }

  void _deleteNotification(int id) {
    setState(() {
      _notifications.removeWhere((n) => n['id'] == id);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم حذف الإشعار')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = _notifications.where((n) => n['read'] == false).length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات'),
        actions: [
          if (unreadCount > 0)
            TextButton(
              onPressed: _markAllAsRead,
              child: const Text(
                'تحديد الكل كمقروء',
                style: TextStyle(color: Colors.white),
              ),
            ),
        ],
      ),
      body: _notifications.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Icon(
                    Icons.notifications_off,
                    size: 80,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'لا توجد إشعارات',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              itemCount: _notifications.length,
              itemBuilder: (context, index) {
                final notification = _notifications[index];
                final isRead = notification['read'] as bool;

                return Dismissible(
                  key: Key(notification['id'].toString()),
                  direction: DismissDirection.endToStart,
                  onDismissed: (direction) {
                    _deleteNotification(notification['id'] as int);
                  },
                  background: Container(
                    color: Colors.red,
                    alignment: Alignment.centerLeft,
                    padding: const EdgeInsets.only(left: 20),
                    child: const Icon(
                      Icons.delete,
                      color: Colors.white,
                    ),
                  ),
                  child: Card(
                    margin: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    color: isRead ? Colors.white : Colors.blue.shade50,
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: notification['color'] as Color,
                        child: Icon(
                          notification['icon'] as IconData,
                          color: Colors.white,
                        ),
                      ),
                      title: Row(
                        children: [
                          Expanded(
                            child: Text(
                              notification['title'] as String,
                              style: TextStyle(
                                fontWeight:
                                    isRead ? FontWeight.normal : FontWeight.bold,
                              ),
                            ),
                          ),
                          if (!isRead)
                            Container(
                              width: 10,
                              height: 10,
                              decoration: const BoxDecoration(
                                color: Colors.blue,
                                shape: BoxShape.circle,
                              ),
                            ),
                        ],
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 4),
                          Text(notification['body'] as String),
                          const SizedBox(height: 4),
                          Text(
                            notification['time'] as String,
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                      onTap: () {
                        if (!isRead) {
                          _markAsRead(notification['id'] as int);
                        }
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('فتح: ${notification['title']}'),
                          ),
                        );
                      },
                    ),
                  ),
                );
              },
            ),
    );
  }
}

// QR Scanner Screen
class QRScannerScreen extends StatelessWidget {
  const QRScannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مسح رمز QR'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.qr_code_scanner,
              size: 120,
              color: Colors.blue,
            ),
            const SizedBox(height: 24),
            const Text(
              'وجه الكاميرا نحو رمز QR',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 48),
            ElevatedButton.icon(
              onPressed: () {
                // TODO: Implement QR scanning with qr_code_scanner package
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم مسح الكود: SN-12345'),
                    duration: Duration(seconds: 2),
                  ),
                );
              },
              icon: const Icon(Icons.camera_alt),
              label: const Text('بدء المسح'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Returns List Screen
class ReturnsListScreen extends StatelessWidget {
  const ReturnsListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final returns = [
      {
        'id': 'RET-001',
        'product': 'لاب توب HP ProBook 450',
        'serial': 'SN-12345',
        'status': 'قيد الفحص',
        'date': '2024-10-24',
        'color': Colors.orange,
      },
      {
        'id': 'RET-002',
        'product': 'طابعة HP LaserJet',
        'serial': 'SN-67890',
        'status': 'قيد الصيانة',
        'date': '2024-10-23',
        'color': Colors.blue,
      },
      {
        'id': 'RET-003',
        'product': 'شاشة Dell 27"',
        'serial': 'SN-54321',
        'status': 'مكتمل',
        'date': '2024-10-22',
        'color': Colors.green,
      },
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('طلبات الإرجاع'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: returns.length,
        itemBuilder: (context, index) {
          final item = returns[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: item['color'] as Color,
                child: const Icon(Icons.assignment_return, color: Colors.white),
              ),
              title: Text(
                item['product'] as String,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${item['id']} - ${item['serial']}'),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.circle,
                        size: 8,
                        color: item['color'] as Color,
                      ),
                      const SizedBox(width: 4),
                      Text(item['status'] as String),
                      const SizedBox(width: 12),
                      const Icon(Icons.calendar_today, size: 12),
                      const SizedBox(width: 4),
                      Text(item['date'] as String),
                    ],
                  ),
                ],
              ),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ReturnDetailScreen(returnItem: item),
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('إنشاء طلب إرجاع جديد')),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

// Return Detail Screen
class ReturnDetailScreen extends StatelessWidget {
  final Map<String, dynamic> returnItem;

  const ReturnDetailScreen({super.key, required this.returnItem});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(returnItem['id'] as String),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      returnItem['product'] as String,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    _DetailRow(
                      icon: Icons.qr_code,
                      label: 'السيريال',
                      value: returnItem['serial'] as String,
                    ),
                    _DetailRow(
                      icon: Icons.info,
                      label: 'الحالة',
                      value: returnItem['status'] as String,
                    ),
                    _DetailRow(
                      icon: Icons.calendar_today,
                      label: 'التاريخ',
                      value: returnItem['date'] as String,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'الإجراءات',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _ActionButton(
              icon: Icons.search,
              label: 'فحص المنتج',
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('بدء الفحص...')),
                );
              },
            ),
            _ActionButton(
              icon: Icons.build,
              label: 'بدء الصيانة',
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('بدء الصيانة...')),
                );
              },
            ),
            _ActionButton(
              icon: Icons.check_circle,
              label: 'إكمال العمل',
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('تم إكمال العمل')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(value),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.all(16),
          alignment: Alignment.centerRight,
        ),
      ),
    );
  }
}

// Work History Screen
class WorkHistoryScreen extends StatelessWidget {
  const WorkHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final history = List.generate(
      10,
      (index) => {
        'date': '2024-10-${24 - index}',
        'jobs': index + 2,
        'hours': (index + 3) * 2,
      },
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل الأعمال'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: history.length,
        itemBuilder: (context, index) {
          final day = history[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: const CircleAvatar(
                backgroundColor: Colors.blue,
                child: Icon(Icons.work, color: Colors.white),
              ),
              title: Text(
                day['date'] as String,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text('${day['jobs']} مهمة - ${day['hours']} ساعة'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('تفاصيل ${day['date']}')),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

// Settings Screen
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _soundEnabled = true;
  bool _vibrationEnabled = true;
  bool _darkMode = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الإعدادات'),
      ),
      body: ListView(
        children: [
          const ListTile(
            title: Text(
              'الإشعارات',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
          ),
          SwitchListTile(
            title: const Text('تفعيل الإشعارات'),
            subtitle: const Text('استقبال إشعارات التطبيق'),
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() {
                _notificationsEnabled = value;
              });
            },
          ),
          SwitchListTile(
            title: const Text('الصوت'),
            subtitle: const Text('تشغيل صوت الإشعارات'),
            value: _soundEnabled,
            onChanged: (value) {
              setState(() {
                _soundEnabled = value;
              });
            },
          ),
          SwitchListTile(
            title: const Text('الاهتزاز'),
            subtitle: const Text('اهتزاز عند الإشعار'),
            value: _vibrationEnabled,
            onChanged: (value) {
              setState(() {
                _vibrationEnabled = value;
              });
            },
          ),
          const Divider(),
          const ListTile(
            title: Text(
              'المظهر',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
          ),
          SwitchListTile(
            title: const Text('الوضع الليلي'),
            subtitle: const Text('تفعيل الثيم الداكن'),
            value: _darkMode,
            onChanged: (value) {
              setState(() {
                _darkMode = value;
              });
            },
          ),
          const Divider(),
          const ListTile(
            title: Text(
              'عن التطبيق',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
          ),
          const ListTile(
            leading: Icon(Icons.info),
            title: Text('الإصدار'),
            subtitle: Text('1.0.0'),
          ),
          const ListTile(
            leading: Icon(Icons.business),
            title: Text('الشركة'),
            subtitle: Text('TSH - Technology Solutions House'),
          ),
        ],
      ),
    );
  }
}
