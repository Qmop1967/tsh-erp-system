class TSHException implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;
  
  const TSHException(
    this.message, {
    this.code,
    this.originalError,
    this.stackTrace,
  });
  
  @override
  String toString() {
    if (code != null) {
      return 'TSHException [$code]: $message';
    }
    return 'TSHException: $message';
  }
}

class ApiException extends TSHException {
  const ApiException(
    String message, {
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'ApiException [$code]: $message';
    }
    return 'ApiException: $message';
  }
}

class NetworkException extends TSHException {
  const NetworkException(
    String message, {
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'NetworkException [$code]: $message';
    }
    return 'NetworkException: $message';
  }
}

class AuthenticationException extends TSHException {
  const AuthenticationException(
    String message, {
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'AuthenticationException [$code]: $message';
    }
    return 'AuthenticationException: $message';
  }
}

class ValidationException extends TSHException {
  final Map<String, List<String>>? fieldErrors;
  
  const ValidationException(
    String message, {
    String? code,
    this.fieldErrors,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'ValidationException [$code]: $message';
    }
    return 'ValidationException: $message';
  }
}

class CacheException extends TSHException {
  const CacheException(
    String message, {
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'CacheException [$code]: $message';
    }
    return 'CacheException: $message';
  }
}

class PermissionException extends TSHException {
  const PermissionException(
    String message, {
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) : super(
    message,
    code: code,
    originalError: originalError,
    stackTrace: stackTrace,
  );
  
  @override
  String toString() {
    if (code != null) {
      return 'PermissionException [$code]: $message';
    }
    return 'PermissionException: $message';
  }
}

// Exception handling utilities
class ExceptionHandler {
  static String getErrorMessage(dynamic error) {
    if (error is TSHException) {
      return error.message;
    }
    
    if (error is FormatException) {
      return 'خطأ في تنسيق البيانات';
    }
    
    if (error is TypeError) {
      return 'خطأ في نوع البيانات';
    }
    
    return 'حدث خطأ غير متوقع';
  }
  
  static String getErrorCode(dynamic error) {
    if (error is TSHException) {
      return error.code ?? 'UNKNOWN_ERROR';
    }
    
    return 'UNKNOWN_ERROR';
  }
  
  static String getLocalizedErrorMessage(dynamic error) {
    if (error is NetworkException) {
      return 'خطأ في الاتصال بالشبكة';
    }
    
    if (error is AuthenticationException) {
      return 'خطأ في المصادقة';
    }
    
    if (error is ApiException) {
      return 'خطأ في النظام';
    }
    
    if (error is ValidationException) {
      return 'خطأ في التحقق من البيانات';
    }
    
    if (error is PermissionException) {
      return 'ليس لديك صلاحية للوصول';
    }
    
    return getErrorMessage(error);
  }
  
  static bool isRetryable(dynamic error) {
    if (error is NetworkException) {
      return true;
    }
    
    if (error is ApiException) {
      final code = error.code;
      return code == 'CONNECTION_TIMEOUT' || 
             code == 'SERVER_ERROR' ||
             code == 'TEMPORARY_ERROR';
    }
    
    return false;
  }
  
  static bool isAuthError(dynamic error) {
    return error is AuthenticationException ||
           (error is ApiException && 
            (error.code == 'AUTH_ERROR' || error.code == 'INVALID_CREDENTIALS'));
  }
  
  static bool isNetworkError(dynamic error) {
    return error is NetworkException;
  }
}
