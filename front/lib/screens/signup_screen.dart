import 'package:flutter/material.dart';
import 'package:front/models/user.dart';
import 'package:front/providers/providers.dart';
import 'package:front/screens/signin_screen.dart';
import 'package:front/services/services.dart';
import 'package:front/utils/utils.dart';
import 'package:provider/provider.dart';

class SignUpPage extends StatefulWidget {
  const SignUpPage({super.key});

  @override
  State<SignUpPage> createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  late TextEditingController _usernameController;
  late TextEditingController _emailController;
  late TextEditingController _passwordController;
  late TextEditingController _confirmPasswordController;
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  Future<void> _signUpSuccess(User userData) async {
    bool isSaveSuccess = await LocalStoreServices.saveInLocal(context, userData);
    if (isSaveSuccess) {
      if (!mounted) return;
      UserProvider userProvider = Provider.of<UserProvider>(context, listen: false);
      userProvider.setUserFromModel(userData);
    }
  }

  void _signUp() async {
    if (_passwordController.text != _confirmPasswordController.text) {
      Utils.showSnackBar(context, 'Password and Confirm Password does not match!');
      return;
    }

    User? userAccount = await AuthService.signUpUser(
      context: context,
      email: _emailController.text,
      username: _usernameController.text,
      password: _passwordController.text,
    );

    if (userAccount != null) {
      await _signUpSuccess(userAccount);
    }
  }

  void _changeToSignIn() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const SignInPage()),
    );
  }

  @override
  void initState() {
    super.initState();
    _usernameController = TextEditingController();
    _emailController = TextEditingController();
    _passwordController = TextEditingController();
    _confirmPasswordController = TextEditingController();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF1F3D2B),
              Color(0xFF3D2914),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: Container(
                  padding: const EdgeInsets.fromLTRB(28, 36, 28, 28),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFFBF5),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.25),
                        blurRadius: 28,
                        offset: const Offset(0, 16),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 72,
                        height: 72,
                        decoration: BoxDecoration(
                          color: const Color(0xFF2E7D4F),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Icon(
                          Icons.coffee_rounded,
                          color: Color(0xFFF6E7C1),
                          size: 38,
                        ),
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'RiExport',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF3D2914),
                          letterSpacing: 0.4,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Café y cacao para la Unión Europea',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF7A6A58),
                        ),
                      ),
                      const SizedBox(height: 28),
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Crear cuenta',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF3D2914),
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      _AuthField(
                        controller: _usernameController,
                        label: 'Usuario',
                        hintText: 'Solo letras',
                        icon: Icons.person_outline_rounded,
                      ),
                      const SizedBox(height: 14),
                      _AuthField(
                        controller: _emailController,
                        label: 'Correo',
                        hintText: 'ejemplo@correo.com',
                        icon: Icons.mail_outline_rounded,
                        keyboardType: TextInputType.emailAddress,
                      ),
                      const SizedBox(height: 14),
                      _AuthField(
                        controller: _passwordController,
                        label: 'Contraseña',
                        hintText: 'Mínimo 8 caracteres',
                        icon: Icons.lock_outline_rounded,
                        obscureText: _obscurePassword,
                        onToggleObscure: () {
                          setState(() => _obscurePassword = !_obscurePassword);
                        },
                      ),
                      const SizedBox(height: 14),
                      _AuthField(
                        controller: _confirmPasswordController,
                        label: 'Confirmar contraseña',
                        hintText: 'Repite la contraseña',
                        icon: Icons.lock_outline_rounded,
                        obscureText: _obscureConfirm,
                        onToggleObscure: () {
                          setState(() => _obscureConfirm = !_obscureConfirm);
                        },
                      ),
                      const SizedBox(height: 26),
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _signUp,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2E7D4F),
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                          child: const Text(
                            'Registrarse',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: _changeToSignIn,
                        child: const Text(
                          '¿Ya tienes cuenta? Iniciar sesión',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: Color(0xFF2E7D4F),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _AuthField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hintText;
  final IconData icon;
  final bool obscureText;
  final VoidCallback? onToggleObscure;
  final TextInputType? keyboardType;

  const _AuthField({
    required this.controller,
    required this.label,
    required this.hintText,
    required this.icon,
    this.obscureText = false,
    this.onToggleObscure,
    this.keyboardType,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Color(0xFF5C3A21),
          ),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            hintText: hintText,
            hintStyle: const TextStyle(color: Color(0xFFA89880), fontSize: 14),
            prefixIcon: Icon(icon, color: const Color(0xFF2E7D4F)),
            suffixIcon: onToggleObscure == null
                ? null
                : IconButton(
                    onPressed: onToggleObscure,
                    icon: Icon(
                      obscureText
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      color: const Color(0xFF7A6A58),
                    ),
                  ),
            filled: true,
            fillColor: const Color(0xFFF3EDE3),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF2E7D4F), width: 1.4),
            ),
          ),
        ),
      ],
    );
  }
}
