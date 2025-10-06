import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'pages/auth/login_page.dart';
import 'pages/dashboard/simple_dashboard.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  runApp(const TSHSalespersonApp());
}

class TSHSalespersonApp extends StatelessWidget {
  const TSHSalespersonApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH Salesperson',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF1B5E20),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B5E20),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Cairo',
      ),
      home: const LoginPage(),
      routes: {
        '/dashboard': (context) => const SimpleDashboard(),
        '/login': (context) => const LoginPage(),
      },
    );
  }
}
