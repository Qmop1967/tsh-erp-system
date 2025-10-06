import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'enhanced_dashboard.dart';
import 'services/auth_service.dart';
import 'utils/theme.dart';
import 'mfa_screens/security_dashboard_screen.dart';

void main() {
  runApp(TSHAdminApp());
}

class TSHAdminApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH Admin Dashboard',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: AuthWrapper(),
      routes: {
        '/login': (context) => LoginScreen(),
        '/dashboard': (context) => EnhancedExecutiveDashboardScreen(),
        '/mfa-security': (context) => SecurityDashboardScreen(),
      },
    );
  }
}

class AuthWrapper extends StatefulWidget {
  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool isAuthenticated = false;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    checkAuthStatus();
  }

  void checkAuthStatus() async {
    try {
      final authService = AuthService();
      final token = await authService.getStoredToken();
      
      if (token != null && token.isNotEmpty) {
        // Verify token with backend
        final isValid = await authService.verifyToken(token);
        setState(() {
          isAuthenticated = isValid;
          isLoading = false;
        });
      } else {
        setState(() {
          isAuthenticated = false;
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        isAuthenticated = false;
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(
                color: Colors.blue,
              ),
              SizedBox(height: 16),
              Text(
                'TSH Admin Dashboard',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Loading...',
                style: TextStyle(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      );
    }

    return isAuthenticated ? EnhancedExecutiveDashboardScreen() : LoginScreen();
  }

class TestHomePage extends StatefulWidget {
  @override
  _TestHomePageState createState() => _TestHomePageState();
}

class _TestHomePageState extends State<TestHomePage> {
  int _counter = 0;
  String _status = "App initialized successfully!";

  void _incrementCounter() {
    setState(() {
      _counter++;
      _status = "Button pressed $_counter time(s)";
    });
    print("Counter: $_counter"); // Debug output
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('TSH Admin Test'),
        backgroundColor: Colors.blue,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Icon(
              Icons.check_circle,
              color: Colors.green,
              size: 64,
            ),
            SizedBox(height: 20),
            Text(
              'Flutter Engine Working!',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.green,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 30),
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                children: [
                  Text(
                    'Status:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    _status,
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.blue.shade800),
                  ),
                ],
              ),
            ),
            SizedBox(height: 30),
            Text(
              'Counter: $_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _incrementCounter,
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
              child: Text(
                'Test Button',
                style: TextStyle(fontSize: 18),
              ),
            ),
            SizedBox(height: 40),
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text(
                      'Device Info:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 8),
                    Text('Platform: iOS'),
                    Text('Bundle ID: com.tsh.admin'),
                    Text('Build Mode: Debug'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),
    );
  }
}
