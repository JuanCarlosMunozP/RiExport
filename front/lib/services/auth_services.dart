import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:front/constants.dart';
import 'package:front/utils/error_handling.dart';
import 'package:front/utils/utils.dart';
import 'package:http/http.dart' as http;
import 'package:front/models/models.dart';

class AuthService {

  static Future<User?> signUpUser({
    required BuildContext context,
    required String email,
    required String username,
    required String password
  }) async {
    try {
      UserAuth userAuth = UserAuth(email,password,username:username);

      http.Response res = await http.post(
        Uri.parse("${Constants.URI}/auth/register"),
        body:userAuth.toJson(),
        headers:<String,String>{
          'Content-Type':'application/json; charset=UTF-8'
        },
      );

      bool hasError = ErrorHandling.httpErrorHandling(response:res,context:context);
      if (hasError) return null;
      return User.fromJson(res.body);
    } catch (e) {
      Utils.showSnackBar(context, e.toString());
      return null;
    }
  }

  static Future<User?> signInUser({
    required BuildContext context,
    required String email,
    required String password,
  }) async {
    try {
      http.Response res = await http.post(
        Uri.parse("${Constants.URI}/auth/login"),
        body: {
          'username': email,
          'password': password,
        },
      );

      bool hasError = ErrorHandling.httpErrorHandling(response: res, context: context);
      if (hasError) return null;

      final data = jsonDecode(res.body) as Map<String, dynamic>;
      return User(
        username: data['username'] ?? '',
        email: email,
        token: data['access_token'] ?? data['token'] ?? '',
      );
    } catch (e) {
      Utils.showSnackBar(context, e.toString());
      return null;
    }
  }

  static Future<User?> getUser({
    required BuildContext context,
    required String token,
  }) async {
    try {
      http.Response res = await http.get(
        Uri.parse("${Constants.URI}/users/me"),
        headers: <String,String>{
          'Content-Type':'application/json; charset=UTF-8',
          'Authorization':'Bearer ${token},'
        },
      );

      if (res.statusCode != 200) return null;

      return User.fromJson(res.body);
    } catch (e) {
      Utils.showSnackBar(context, e.toString());
      return null;
    }
  }
}