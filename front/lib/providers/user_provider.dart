import 'package:flutter/material.dart';
import 'package:front/models/user.dart';

class UserProvider extends ChangeNotifier {
  User? _user;

  User? get user => _user;

  void setUserFromJson(String user) {
    _user = User.fromJson(user);
    notifyListeners();
  }

  void setUserFromModel(User user) {
    _user = user;
    notifyListeners();
  }

  void setUserNull() {
    _user = null;
    notifyListeners();
  }
}