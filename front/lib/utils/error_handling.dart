import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'utils.dart';

class ErrorHandling {

  static String _messageFromBody(String body) {
    try {
      final decoded = jsonDecode(body);
      if (decoded is String) return decoded;
      if (decoded is Map && decoded['detail'] != null) {
        final detail = decoded['detail'];
        if (detail is String) return detail;
        return detail.toString();
      }
      return decoded.toString();
    } catch (_) {
      return body;
    }
  }

  static bool httpErrorHandling({
    required http.Response response,
    required BuildContext context,
  }) {
    switch(response.statusCode) {
      case 200:
      case 201:
        return false;
      case 400:
      case 401:
      case 404:
      default:
        Utils.showSnackBar(context, _messageFromBody(response.body));
        return true;
    }
  }
}