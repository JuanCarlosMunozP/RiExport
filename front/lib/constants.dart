import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;

class Constants {
  static String get URI {
    if (kIsWeb) {
      return 'http://localhost:8081';
    }
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8081';
    }
    return 'http://localhost:8081';
  }

  static const String LOCAL_STORAGE_TOKEN_KEY = "user-data-token";
}
