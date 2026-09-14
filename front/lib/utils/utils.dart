import 'package:flutter/material.dart';

class Utils {
  static void showSnackBar(BuildContext context,String text) {
    final messenger = ScaffoldMessenger.maybeOf(context);
    if (messenger == null) return;
    messenger.showSnackBar(SnackBar(content: Text(text)));
  }
}