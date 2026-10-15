import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiConfig {
  static const String defaultBaseUrl = 'http://127.0.0.1:8000';
  static const String _storageKeyBaseUrl = 'api_base_url';
  static const String _storageKeyToken = 'jwt_access_token';

  static final FlutterSecureStorage _storage = const FlutterSecureStorage();
  static String currentBaseUrl = defaultBaseUrl;
  static String? currentToken;

  static Future<void> initialize() async {
    try {
      final savedUrl = await _storage.read(key: _storageKeyBaseUrl);
      if (savedUrl != null && savedUrl.isNotEmpty) {
        currentBaseUrl = savedUrl;
      }
      currentToken = await _storage.read(key: _storageKeyToken);
    } catch (_) {
      currentBaseUrl = defaultBaseUrl;
    }
  }

  static Future<void> setBaseUrl(String url) async {
    currentBaseUrl = url.trim().replaceAll(RegExp(r'/+$'), '');
    await _storage.write(key: _storageKeyBaseUrl, value: currentBaseUrl);
  }

  static Future<void> setToken(String? token) async {
    currentToken = token;
    if (token != null) {
      await _storage.write(key: _storageKeyToken, value: token);
    } else {
      await _storage.delete(key: _storageKeyToken);
    }
  }

  static bool get isAuthenticated => currentToken != null && currentToken!.isNotEmpty;
}
