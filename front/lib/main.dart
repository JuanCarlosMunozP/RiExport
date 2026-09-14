import 'package:flutter/material.dart';
import 'package:front/models/models.dart';
import 'package:front/providers/user_provider.dart';
import 'package:front/screens/home_screen.dart';
import 'package:front/screens/signup_screen.dart';
import 'package:front/services/services.dart';
import 'package:provider/provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    ChangeNotifierProvider<UserProvider>(
      create: (context) => UserProvider(),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override 
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  void _getUserData() async {
    String? existedToken = await LocalStoreServices.getFromLocal(context);
    if (existedToken != null) {
      User? user = await AuthService.getUser(context:context, token:existedToken);
      if (user != null) {
        if (!mounted) return null;
        Provider.of<UserProvider>(context,listen:false).setUserFromModel(user);
      }
    }
  }

  @override 
  void initState() {
    super.initState();
    _getUserData();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title:'App de exportaciones de cafe y cacao para la Union europa',
      theme:ThemeData(
        primarySwatch: Colors.blue,
      ),
      home:Consumer<UserProvider>(builder: (context,userProvider,child) {
        if (userProvider.user != null) {
          return const HomePage();
        }
        return const SignUpPage();
      },
      )
    );
  }
}


