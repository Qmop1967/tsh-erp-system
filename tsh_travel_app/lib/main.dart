import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:get_it/get_it.dart';
import 'package:provider/provider.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

import 'core/di/service_locator.dart';
import 'core/router/app_router.dart';
import 'features/auth/presentation/blocs/auth_bloc.dart';
import 'features/dashboard/presentation/blocs/dashboard_bloc.dart';
import 'features/customers/presentation/blocs/customers_bloc.dart';
import 'features/profile/presentation/blocs/profile_bloc.dart';

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
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (context) => LocaleService(),
        ),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider(
            create: (context) => GetIt.instance<AuthBloc>()..add(AuthCheckRequested()),
          ),
          BlocProvider(
            create: (context) => GetIt.instance<DashboardBloc>(),
          ),
          BlocProvider(
            create: (context) => CustomersBloc(),
          ),
          BlocProvider(
            create: (context) => ProfileBloc(),
          ),
        ],
        child: Consumer<LocaleService>(
          builder: (context, localeService, child) {
            return MaterialApp.router(
              title: 'TSH Travel Sales',
              theme: AppTheme.lightTheme,
              darkTheme: AppTheme.darkTheme,
              routerConfig: AppRouter.router,
              debugShowCheckedModeBanner: false,
              locale: localeService.currentLocale,
              // Add localization support
              localizationsDelegates: const [
                AppLocalizations.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              supportedLocales: AppLocalizations.supportedLocales,
            );
          },
        ),
      ),
    );
  }
}
