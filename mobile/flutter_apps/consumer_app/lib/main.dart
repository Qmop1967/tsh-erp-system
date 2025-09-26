import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Import TSH Core Design System
import 'package:tsh_core_package/tsh_core_package.dart';

void main() {
  runApp(const TSHConsumerApp());
}

class TSHConsumerApp extends StatelessWidget {
  const TSHConsumerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => LanguageService(),
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Consumer App',
            theme: TSHTheme.lightTheme,
            darkTheme: TSHTheme.darkTheme,
            themeMode: languageService.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            locale: languageService.currentLocale,
            localizationsDelegates: const [
              TSHLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: TSHLocalizations.supportedLocales,
            home: const ConsumerMainScreen(),
            debugShowCheckedModeBanner: false,
            builder: (context, child) {
              return Directionality(
                textDirection: languageService.isRTL 
                    ? TextDirection.rtl 
                    : TextDirection.ltr,
                child: child!,
              );
            },
          );
        },
      ),
    );
  }
}

class ConsumerMainScreen extends StatefulWidget {
  const ConsumerMainScreen({super.key});

  @override
  State<ConsumerMainScreen> createState() => _ConsumerMainScreenState();
}

class _ConsumerMainScreenState extends State<ConsumerMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const ConsumerShopScreen(),
    const ProductCatalogScreen(),
    const MyOrdersScreen(),
    const MyAccountScreen(),
    const SupportScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Row(
          children: [
            TSHTheme.tshLogo(height: 35),
            const SizedBox(width: 12),
            Text(localizations.translate('tsh_consumer_app')),
          ],
        ),
        subtitle: Text(
          'Electronics Shopping',
          style: TSHTheme.bodySmall.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
        ),
        actions: [
          // Shopping Cart
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.shopping_cart),
                Positioned(
                  right: 0,
                  top: 0,
                  child: Container(
                    padding: const EdgeInsets.all(1),
                    decoration: BoxDecoration(
                      color: TSHTheme.accentOrange,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 16,
                      minHeight: 16,
                    ),
                    child: const Text(
                      '3',
                      style: TextStyle(
                        color: TSHTheme.surfaceWhite,
                        fontSize: 12,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ],
            ),
            onPressed: () {},
          ),
          // Language Toggle
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              border: Border.all(color: TSHTheme.surfaceWhite.withOpacity(0.3)),
              borderRadius: BorderRadius.circular(6),
            ),
            child: TextButton(
              onPressed: () => languageService.toggleLanguage(),
              child: Text(
                languageService.currentLocale.languageCode == 'en' ? 'عربي' : 'EN',
                style: const TextStyle(
                  color: TSHTheme.surfaceWhite,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          // Dark Mode Toggle
          IconButton(
            icon: Icon(
              languageService.isDarkMode ? Icons.light_mode : Icons.dark_mode,
              color: TSHTheme.surfaceWhite,
            ),
            onPressed: () => languageService.toggleDarkMode(),
          ),
        ],
      ),
      
      body: _screens[_selectedIndex],
      
      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.shopping_bag),
            label: 'Shop',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.category),
            label: localizations.translate('products'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.receipt_long),
            label: localizations.translate('orders'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: 'Account',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.support_agent),
            label: 'Support',
          ),
        ],
      ),
    );
  }
}

// ===============================================
// CONSUMER SHOP SCREEN - Main Shopping Interface
// ===============================================
class ConsumerShopScreen extends StatefulWidget {
  const ConsumerShopScreen({super.key});

  @override
  State<ConsumerShopScreen> createState() => _ConsumerShopScreenState();
}

class _ConsumerShopScreenState extends State<ConsumerShopScreen> {
  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          localizations.translate('welcome_message'),
                          style: TSHTheme.headingMedium,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Shop Electronics Online',
                          style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.textLight),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {},
                          child: Text('Start Shopping'),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: TSHTheme.primaryTeal.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.shopping_bag,
                      size: 48,
                      color: TSHTheme.primaryTeal,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // Featured Categories
          Text(
            'Featured Categories',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.2,
            children: [
              _buildCategoryCard('Laptop Accessories', Icons.laptop, TSHTheme.primaryBlue),
              _buildCategoryCard('Mobile Accessories', Icons.smartphone, TSHTheme.primaryTeal),
              _buildCategoryCard('Printer Accessories', Icons.print, TSHTheme.successGreen),
              _buildCategoryCard('Network Equipment', Icons.router, TSHTheme.accentOrange),
            ],
          ),
          const SizedBox(height: 24),
          
          // Special Offers
          Text(
            'Special Offers',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: 5,
              itemBuilder: (context, index) {
                return Container(
                  width: 150,
                  margin: const EdgeInsets.only(right: 12),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            height: 80,
                            decoration: BoxDecoration(
                              color: TSHTheme.primaryTeal.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Center(
                              child: Icon(Icons.devices, size: 40, color: TSHTheme.primaryTeal),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Product ${index + 1}',
                            style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${25000 + (index * 5000)} IQD',
                            style: TSHTheme.bodySmall.copyWith(color: TSHTheme.primaryTeal),
                          ),
                          const Spacer(),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: () {},
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 8),
                              ),
                              child: const Text('Add to Cart', style: TextStyle(fontSize: 12)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(String title, IconData icon, Color color) {
    return Card(
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 32,
                  color: color,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ===============================================
// PLACEHOLDER SCREENS FOR OTHER CONSUMER SECTIONS
// ===============================================
class ProductCatalogScreen extends StatelessWidget {
  const ProductCatalogScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Product Catalog - Consumer Shopping'));
  }
}

class MyOrdersScreen extends StatelessWidget {
  const MyOrdersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('My Orders - Order History'));
  }
}

class MyAccountScreen extends StatelessWidget {
  const MyAccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('My Account - Consumer Profile'));
  }
}

class SupportScreen extends StatelessWidget {
  const SupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Customer Support - 24/7 AI Assistant'));
  }
}
