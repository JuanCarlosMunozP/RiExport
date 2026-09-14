import 'package:flutter/material.dart';
import 'package:front/constants.dart';
import 'package:front/models/user.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocalStoreServices {
  static final SharedPreferencesAsync _prefs = SharedPreferencesAsync();
  static String? _memoryToken;

  static Future<bool> saveInLocal(BuildContext context, User userData) async {
    _memoryToken = userData.token;
    try {
      await _prefs.setString(Constants.LOCAL_STORAGE_TOKEN_KEY, userData.token);
      return true;
    } catch (e) {
      return _memoryToken != null;
    }
  }

  static Future<bool> removeFromLocal(BuildContext context) async {
    _memoryToken = null;
    try {
      await _prefs.remove(Constants.LOCAL_STORAGE_TOKEN_KEY);
      return true;
    } catch (e) {
      return true;
    }
  }

  static Future<String?> getFromLocal(BuildContext context) async {
    try {
      final stored = await _prefs.getString(Constants.LOCAL_STORAGE_TOKEN_KEY);
      if (stored != null) {
        _memoryToken = stored;
        return stored;
      }
      return _memoryToken;
    } catch (e) {
      return _memoryToken;
    }
  }
}
