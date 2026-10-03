import 'package:flutter/foundation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_exception.dart';

class AuthSession extends ChangeNotifier {
  String? _accessToken;

  String? get accessToken => _accessToken;
  bool get isAuthenticated => _accessToken != null;

  Future<void> authenticate(
    ApiClient apiClient, {
    required String email,
    required String password,
  }) async {
    final response = await apiClient.post(
      '/auth/login',
      body: {'email': email.trim(), 'password': password},
    );
    if (response is! Map<String, dynamic> ||
        response['access_token'] is! String ||
        (response['access_token'] as String).isEmpty ||
        response['token_type'] is! String ||
        (response['token_type'] as String).toLowerCase() != 'bearer') {
      throw const ApiException(
        code: 'INVALID_RESPONSE',
        message:
            'El servidor devolvió una respuesta de autenticación no válida.',
      );
    }
    _accessToken = response['access_token'] as String;
    notifyListeners();
  }

  void clear() {
    _accessToken = null;
    notifyListeners();
  }
}
