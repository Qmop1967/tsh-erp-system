import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

import 'core/di/service_locator.dart';
import 'core/router/app_router.dart';
import 'features/auth/presentation/blocs/auth_bloc.dart';
import 'features/dashboard/presentation/blocs/dashboard_bloc.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Setup dependency injection
  await setupServiceLocator();
  
  runApp(const TravelSalesApp());
}

class TravelSalesApp extends StatelessWidget {
  const TravelSalesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (context) => GetIt.instance<AuthBloc>()..add(AuthCheckRequested()),
        ),
        BlocProvider(
          create: (context) => GetIt.instance<DashboardBloc>(),
        ),
      ],
      child: MaterialApp.router(
        title: 'TSH Travel Sales',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        routerConfig: AppRouter.router,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
