import 'package:get_it/get_it.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import '../../features/auth/presentation/blocs/auth_bloc.dart';
import '../../features/dashboard/presentation/blocs/dashboard_bloc.dart';

final getIt = GetIt.instance;

Future<void> setupServiceLocator() async {
  // Core services
  getIt.registerLazySingleton<StorageService>(() => StorageService());
  getIt.registerLazySingleton<ConnectivityService>(() => ConnectivityService());
  getIt.registerLazySingleton<ApiService>(() => ApiService());
  getIt.registerLazySingleton<LocaleService>(() => LocaleService());
  
  getIt.registerLazySingleton<AuthService>(
    () => AuthService(getIt<ApiService>(), getIt<StorageService>()),
  );

  // Initialize connectivity service
  await getIt<ConnectivityService>().initialize();

  // Blocs
  getIt.registerFactory<AuthBloc>(
    () => AuthBloc(getIt<AuthService>()),
  );
  
  getIt.registerFactory<DashboardBloc>(
    () => DashboardBloc(getIt<AuthService>()),
  );
}
