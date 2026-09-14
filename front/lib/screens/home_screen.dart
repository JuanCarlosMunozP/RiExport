import 'package:flutter/material.dart';
import 'package:front/providers/providers.dart';
import 'package:front/services/services.dart';
import 'package:front/widgets/custom_elevated_button.dart';
import 'package:provider/provider.dart';

class HomePage extends StatefulWidget{
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();

}
class _HomePageState extends State<HomePage> {
  void _logOut() async {
    bool removeSuccess = await LocalStoreServices.removeFromLocal(context);
    if (removeSuccess) {
      if (!mounted) return;
      Provider.of<UserProvider>(context,listen:false).setUserNull();
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<UserProvider>().user;
    
    if (user == null) {
      return const Center(child:CircularProgressIndicator());
    }

    return Scaffold(
      body:Center(
        child:Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text("Home Page",style:TextStyle(fontSize:28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 35),

            Text("Username: ${user.username}",style:const TextStyle(fontSize:18)),
            const SizedBox(height: 15),

            Text("Email: ${user.email}",style:const TextStyle(fontSize:18)),
            const SizedBox(height: 15),

            CustomElevatedButton(
              onPressfunc: _logOut,
              buttonText: "Log out",
            )
          ]
        )
      )
    );
  }
}
