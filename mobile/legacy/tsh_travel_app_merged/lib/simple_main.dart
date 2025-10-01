import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'features/customers/presentation/blocs/customers_bloc.dart';
import 'features/profile/presentation/blocs/profile_bloc.dart';

void main() {
  runApp(const SimpleTSHApp());
}

class SimpleTSHApp extends StatelessWidget {
  const SimpleTSHApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => CustomersBloc()),
        BlocProvider(create: (context) => ProfileBloc()),
      ],
      child: MaterialApp(
        title: 'TSH Travel Sales - Demo',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
          useMaterial3: true,
        ),
        home: const TSHDemoPage(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class TSHDemoPage extends StatefulWidget {
  const TSHDemoPage({super.key});

  @override
  State<TSHDemoPage> createState() => _TSHDemoPageState();
}

class _TSHDemoPageState extends State<TSHDemoPage> {
  int _currentIndex = 0;
  final PageController _pageController = PageController();

  final List<Widget> _pages = const [
    DemoHomePage(),
    DemoCustomersWrapper(),
    DemoProfileWrapper(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TSH Travel Sales'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: PageView(
        controller: _pageController,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
          _pageController.animateToPage(
            index,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
          );
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: 'Customers',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class DemoHomePage extends StatelessWidget {
  const DemoHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome to TSH Travel Sales',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Complete Travel Salesperson App with modern Flutter UI',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Features Implemented:',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  const FeatureItem(
                    icon: Icons.people,
                    title: 'Customer Management',
                    description: 'Add, edit, search, and filter customers',
                  ),
                  const FeatureItem(
                    icon: Icons.person,
                    title: 'User Profile',
                    description: 'Profile management with stats and settings',
                  ),
                  const FeatureItem(
                    icon: Icons.shopping_cart,
                    title: 'Sales & Orders',
                    description: 'Complete sales workflow (implemented in previous pages)',
                  ),
                  const FeatureItem(
                    icon: Icons.inventory,
                    title: 'Product Management',
                    description: 'Product catalog with search and filtering',
                  ),
                  const FeatureItem(
                    icon: Icons.dashboard,
                    title: 'Dashboard',
                    description: 'Analytics and performance metrics',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            color: Colors.green.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green.shade600),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'App Ready for Preview!',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Colors.green.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Navigate through the tabs to explore all features.',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.green.shade600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class FeatureItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const FeatureItem({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class DemoCustomersWrapper extends StatelessWidget {
  const DemoCustomersWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return const SimpleCustomersPage();
  }
}

class DemoProfileWrapper extends StatelessWidget {
  const DemoProfileWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return const SimpleProfilePage();
  }
}

// Simplified versions of the pages that don't depend on the core package
class SimpleCustomersPage extends StatefulWidget {
  const SimpleCustomersPage({super.key});

  @override
  State<SimpleCustomersPage> createState() => _SimpleCustomersPageState();
}

class _SimpleCustomersPageState extends State<SimpleCustomersPage> {
  @override
  void initState() {
    super.initState();
    context.read<CustomersBloc>().add(LoadCustomers());
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Customers',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: BlocBuilder<CustomersBloc, CustomersState>(
              builder: (context, state) {
                if (state is CustomersLoading) {
                  return const Center(child: CircularProgressIndicator());
                } else if (state is CustomersLoaded) {
                  return ListView.builder(
                    itemCount: state.filteredCustomers.length,
                    itemBuilder: (context, index) {
                      final customer = state.filteredCustomers[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            child: Text(customer.name.substring(0, 2)),
                          ),
                          title: Text(customer.name),
                          subtitle: Text(customer.email),
                          trailing: Text('\$${customer.totalPurchases.toStringAsFixed(2)}'),
                        ),
                      );
                    },
                  );
                } else if (state is CustomersError) {
                  return Center(child: Text('Error: ${state.message}'));
                }
                return const Center(child: Text('No customers found'));
              },
            ),
          ),
        ],
      ),
    );
  }
}

class SimpleProfilePage extends StatefulWidget {
  const SimpleProfilePage({super.key});

  @override
  State<SimpleProfilePage> createState() => _SimpleProfilePageState();
}

class _SimpleProfilePageState extends State<SimpleProfilePage> {
  @override
  void initState() {
    super.initState();
    context.read<ProfileBloc>().add(LoadProfile());
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: BlocBuilder<ProfileBloc, ProfileState>(
        builder: (context, state) {
          if (state is ProfileLoading) {
            return const Center(child: CircularProgressIndicator());
          } else if (state is ProfileLoaded) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 30,
                          child: Text(state.user.fullName.substring(0, 2)),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                state.user.fullName,
                                style: Theme.of(context).textTheme.titleLarge,
                              ),
                              Text(state.user.email),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Performance Stats',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: _buildStatItem(
                                context,
                                'Total Sales',
                                state.stats.totalSales.toString(),
                                Icons.shopping_cart,
                              ),
                            ),
                            Expanded(
                              child: _buildStatItem(
                                context,
                                'Revenue',
                                '\$${state.stats.totalRevenue.toStringAsFixed(0)}',
                                Icons.attach_money,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          } else if (state is ProfileError) {
            return Center(child: Text('Error: ${state.message}'));
          }
          return const Center(child: Text('Loading profile...'));
        },
      ),
    );
  }

  Widget _buildStatItem(BuildContext context, String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 32, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}
