import 'package:flutter/widgets.dart';

import 'app/app.dart';
import 'features/auth/state/auth_session.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final authSession = AuthSession();
  await authSession.restore();
  runApp(RiExportApp(authSession: authSession));
}
