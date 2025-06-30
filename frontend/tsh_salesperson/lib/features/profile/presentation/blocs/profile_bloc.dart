import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

// Events
abstract class ProfileEvent extends Equatable {
  const ProfileEvent();

  @override
  List<Object?> get props => [];
}

class LoadProfile extends ProfileEvent {}

class UpdateProfile extends ProfileEvent {
  final User user;

  const UpdateProfile(this.user);

  @override
  List<Object?> get props => [user];
}

class ChangePassword extends ProfileEvent {
  final String currentPassword;
  final String newPassword;

  const ChangePassword({
    required this.currentPassword,
    required this.newPassword,
  });

  @override
  List<Object?> get props => [currentPassword, newPassword];
}

class UpdateSettings extends ProfileEvent {
  final ProfileSettings settings;

  const UpdateSettings(this.settings);

  @override
  List<Object?> get props => [settings];
}

class LogoutUser extends ProfileEvent {}

// States
abstract class ProfileState extends Equatable {
  const ProfileState();

  @override
  List<Object?> get props => [];
}

class ProfileInitial extends ProfileState {}

class ProfileLoading extends ProfileState {}

class ProfileLoaded extends ProfileState {
  final User user;
  final ProfileSettings settings;
  final ProfileStats stats;

  const ProfileLoaded({
    required this.user,
    required this.settings,
    required this.stats,
  });

  @override
  List<Object?> get props => [user, settings, stats];

  ProfileLoaded copyWith({
    User? user,
    ProfileSettings? settings,
    ProfileStats? stats,
  }) {
    return ProfileLoaded(
      user: user ?? this.user,
      settings: settings ?? this.settings,
      stats: stats ?? this.stats,
    );
  }
}

class ProfileError extends ProfileState {
  final String message;

  const ProfileError(this.message);

  @override
  List<Object?> get props => [message];
}

class PasswordChangeSuccess extends ProfileState {}

class LogoutSuccess extends ProfileState {}

// Profile Settings Model
class ProfileSettings extends Equatable {
  final bool notifications;
  final bool darkMode;
  final String language;
  final String currency;
  final bool locationTracking;
  final bool offlineSync;

  const ProfileSettings({
    required this.notifications,
    required this.darkMode,
    required this.language,
    required this.currency,
    required this.locationTracking,
    required this.offlineSync,
  });

  @override
  List<Object?> get props => [
        notifications,
        darkMode,
        language,
        currency,
        locationTracking,
        offlineSync,
      ];

  ProfileSettings copyWith({
    bool? notifications,
    bool? darkMode,
    String? language,
    String? currency,
    bool? locationTracking,
    bool? offlineSync,
  }) {
    return ProfileSettings(
      notifications: notifications ?? this.notifications,
      darkMode: darkMode ?? this.darkMode,
      language: language ?? this.language,
      currency: currency ?? this.currency,
      locationTracking: locationTracking ?? this.locationTracking,
      offlineSync: offlineSync ?? this.offlineSync,
    );
  }
}

// Profile Stats Model
class ProfileStats extends Equatable {
  final int totalSales;
  final double totalRevenue;
  final int activeCustomers;
  final int ordersThisMonth;
  final double averageOrderValue;
  final int daysActive;

  const ProfileStats({
    required this.totalSales,
    required this.totalRevenue,
    required this.activeCustomers,
    required this.ordersThisMonth,
    required this.averageOrderValue,
    required this.daysActive,
  });

  @override
  List<Object?> get props => [
        totalSales,
        totalRevenue,
        activeCustomers,
        ordersThisMonth,
        averageOrderValue,
        daysActive,
      ];
}

// BLoC
class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  ProfileBloc() : super(ProfileInitial()) {
    on<LoadProfile>(_onLoadProfile);
    on<UpdateProfile>(_onUpdateProfile);
    on<ChangePassword>(_onChangePassword);
    on<UpdateSettings>(_onUpdateSettings);
    on<LogoutUser>(_onLogoutUser);
  }

  Future<void> _onLoadProfile(
    LoadProfile event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    
    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Mock user data
      final user = User(
        id: 1,
        email: 'salesperson@tsh.ae',
        firstName: 'Ahmed',
        lastName: 'Al-Mansouri',
        isActive: true,
        createdAt: DateTime.now().subtract(const Duration(days: 365)),
        updatedAt: DateTime.now(),
      );

      // Mock settings
      const settings = ProfileSettings(
        notifications: true,
        darkMode: false,
        language: 'English',
        currency: 'AED',
        locationTracking: true,
        offlineSync: true,
      );

      // Mock stats
      const stats = ProfileStats(
        totalSales: 247,
        totalRevenue: 156750.50,
        activeCustomers: 85,
        ordersThisMonth: 23,
        averageOrderValue: 634.55,
        daysActive: 365,
      );

      emit(ProfileLoaded(
        user: user,
        settings: settings,
        stats: stats,
      ));
    } catch (e) {
      emit(ProfileError('Failed to load profile: ${e.toString()}'));
    }
  }

  Future<void> _onUpdateProfile(
    UpdateProfile event,
    Emitter<ProfileState> emit,
  ) async {
    if (state is ProfileLoaded) {
      final currentState = state as ProfileLoaded;
      emit(ProfileLoading());
      
      try {
        // Simulate API call
        await Future.delayed(const Duration(milliseconds: 800));
        
        emit(currentState.copyWith(user: event.user));
      } catch (e) {
        emit(ProfileError('Failed to update profile: ${e.toString()}'));
      }
    }
  }

  Future<void> _onChangePassword(
    ChangePassword event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    
    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 1000));
      
      // In a real app, you would validate the current password
      // and update it on the server
      
      emit(PasswordChangeSuccess());
    } catch (e) {
      emit(ProfileError('Failed to change password: ${e.toString()}'));
    }
  }

  Future<void> _onUpdateSettings(
    UpdateSettings event,
    Emitter<ProfileState> emit,
  ) async {
    if (state is ProfileLoaded) {
      final currentState = state as ProfileLoaded;
      
      try {
        // Simulate API call
        await Future.delayed(const Duration(milliseconds: 300));
        
        emit(currentState.copyWith(settings: event.settings));
      } catch (e) {
        emit(ProfileError('Failed to update settings: ${e.toString()}'));
      }
    }
  }

  Future<void> _onLogoutUser(
    LogoutUser event,
    Emitter<ProfileState> emit,
  ) async {
    emit(ProfileLoading());
    
    try {
      // Simulate logout process
      await Future.delayed(const Duration(milliseconds: 500));
      
      // In a real app, you would:
      // - Clear local storage
      // - Invalidate tokens
      // - Clear user session
      
      emit(LogoutSuccess());
    } catch (e) {
      emit(ProfileError('Failed to logout: ${e.toString()}'));
    }
  }
}
