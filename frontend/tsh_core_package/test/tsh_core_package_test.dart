import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

void main() {
  test('TSH Core Package exports are accessible', () {
    // Test that our main exports are accessible
    expect(AppColors.primary, isA<Color>());
    expect(AppTheme.lightTheme, isA<ThemeData>());
    expect(AppTheme.darkTheme, isA<ThemeData>());
  });

  test('User model can be created', () {
    final user = User(
      id: 1,
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'User',
      isActive: true,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    expect(user.id, 1);
    expect(user.firstName, 'Test');
    expect(user.lastName, 'User');
    expect(user.email, 'test@example.com');
    expect(user.isActive, true);
  });
}
