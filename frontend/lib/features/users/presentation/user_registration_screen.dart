import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/api/api_exception.dart';

class UserRegistrationScreen extends StatefulWidget {
  const UserRegistrationScreen({super.key, required this.onRegister});

  final Future<void> Function(Map<String, Object?> request) onRegister;

  @override
  State<UserRegistrationScreen> createState() => _UserRegistrationScreenState();
}

class _UserRegistrationScreenState extends State<UserRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmationController = TextEditingController();
  final _roleIdController = TextEditingController();
  bool _hidePassword = true;
  bool _hideConfirmation = true;
  bool _isSubmitting = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmationController.dispose();
    _roleIdController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    if (!_formKey.currentState!.validate()) return;

    final phone = _phoneController.text.trim();
    final request = <String, Object?>{
      'email': _emailController.text.trim(),
      'password': _passwordController.text,
      'first_name': _firstNameController.text.trim(),
      'last_name': _lastNameController.text.trim(),
      'role_id': int.parse(_roleIdController.text),
      if (phone.isNotEmpty) 'phone': phone,
    };

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _successMessage = null;
    });
    try {
      await widget.onRegister(request);
      if (!mounted) return;
      _formKey.currentState!.reset();
      _firstNameController.clear();
      _lastNameController.clear();
      _emailController.clear();
      _phoneController.clear();
      _passwordController.clear();
      _confirmationController.clear();
      _roleIdController.clear();
      setState(() => _successMessage = 'Usuario registrado correctamente.');
    } on ApiException catch (error) {
      if (mounted) setState(() => _errorMessage = error.message);
    } catch (_) {
      if (mounted) {
        setState(() {
          _errorMessage =
              'No fue posible registrar el usuario. Inténtalo de nuevo.';
        });
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFF6F5F0),
    appBar: AppBar(
      title: const Text('Registrar usuario'),
      backgroundColor: const Color(0xFFF6F5F0),
    ),
    body: SafeArea(
      top: false,
      child: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 40),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: _buildForm(context, wide: constraints.maxWidth >= 600),
            ),
          ),
        ),
      ),
    ),
  );

  Widget _buildForm(BuildContext context, {required bool wide}) {
    final textTheme = Theme.of(context).textTheme;
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Datos de la cuenta',
            style: textTheme.headlineSmall?.copyWith(
              color: const Color(0xFF193D35),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Completa la información para crear el acceso.',
            style: textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF68736E),
            ),
          ),
          const SizedBox(height: 28),
          _fieldRow(
            wide: wide,
            left: _textField(
              label: 'Nombres',
              controller: _firstNameController,
              hint: 'Nombres',
              validator: _requiredName,
              textCapitalization: TextCapitalization.words,
              autofillHints: const [AutofillHints.givenName],
            ),
            right: _textField(
              label: 'Apellidos',
              controller: _lastNameController,
              hint: 'Apellidos',
              validator: _requiredName,
              textCapitalization: TextCapitalization.words,
              autofillHints: const [AutofillHints.familyName],
            ),
          ),
          const SizedBox(height: 18),
          _fieldRow(
            wide: wide,
            left: _textField(
              label: 'Correo electrónico',
              controller: _emailController,
              hint: 'nombre@empresa.com',
              keyboardType: TextInputType.emailAddress,
              autofillHints: const [AutofillHints.email],
              validator: (value) {
                final email = value?.trim() ?? '';
                if (email.isEmpty) return 'Ingresa el correo electrónico.';
                if (!RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email)) {
                  return 'Ingresa un correo válido.';
                }
                return null;
              },
            ),
            right: _textField(
              label: 'Teléfono (opcional)',
              controller: _phoneController,
              hint: '+57 300 123 4567',
              keyboardType: TextInputType.phone,
            ),
          ),
          const SizedBox(height: 18),
          _fieldRow(
            wide: wide,
            left: _textField(
              label: 'Contraseña',
              controller: _passwordController,
              hint: 'Contraseña',
              obscureText: _hidePassword,
              autofillHints: const [AutofillHints.newPassword],
              suffix: _visibilityButton(
                hidden: _hidePassword,
                onPressed: () => setState(() => _hidePassword = !_hidePassword),
                showTooltip: 'Mostrar contraseña',
                hideTooltip: 'Ocultar contraseña',
              ),
              validator: (value) {
                final password = value ?? '';
                if (password.isEmpty) return 'Ingresa una contraseña.';
                if (password.contains('\x00') ||
                    utf8.encode(password).length > 72) {
                  return 'La contraseña debe ocupar máximo 72 bytes UTF-8.';
                }
                return null;
              },
            ),
            right: _textField(
              label: 'Confirmar contraseña',
              controller: _confirmationController,
              hint: 'Repite la contraseña',
              obscureText: _hideConfirmation,
              autofillHints: const [AutofillHints.newPassword],
              suffix: _visibilityButton(
                hidden: _hideConfirmation,
                onPressed: () =>
                    setState(() => _hideConfirmation = !_hideConfirmation),
                showTooltip: 'Mostrar confirmación',
                hideTooltip: 'Ocultar confirmación',
              ),
              validator: (value) {
                if ((value ?? '').isEmpty) return 'Confirma la contraseña.';
                if (value != _passwordController.text) {
                  return 'Las contraseñas no coinciden.';
                }
                return null;
              },
            ),
          ),
          const SizedBox(height: 18),
          _textField(
            label: 'ID del rol activo',
            controller: _roleIdController,
            hint: 'ID numérico',
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            validator: (value) {
              final roleId = int.tryParse(value ?? '');
              if (roleId == null || roleId < 1) {
                return 'Ingresa un ID de rol válido.';
              }
              return null;
            },
          ),
          if (_errorMessage != null) ...[
            const SizedBox(height: 18),
            _StatusBanner(message: _errorMessage!, isError: true),
          ],
          if (_successMessage != null) ...[
            const SizedBox(height: 18),
            _StatusBanner(message: _successMessage!, isError: false),
          ],
          const SizedBox(height: 26),
          SizedBox(
            height: 52,
            child: FilledButton.icon(
              onPressed: _isSubmitting ? null : _submit,
              icon: _isSubmitting
                  ? const SizedBox.square(
                      dimension: 19,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.person_add_alt_1_rounded),
              label: Text(_isSubmitting ? 'Registrando…' : 'Crear usuario'),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF193D35),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _fieldRow({
    required bool wide,
    required Widget left,
    required Widget right,
  }) => wide
      ? Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: left),
            const SizedBox(width: 18),
            Expanded(child: right),
          ],
        )
      : Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [left, const SizedBox(height: 18), right],
        );

  Widget _textField({
    required String label,
    required TextEditingController controller,
    required String hint,
    String? Function(String?)? validator,
    TextInputType? keyboardType,
    TextCapitalization textCapitalization = TextCapitalization.none,
    List<String>? autofillHints,
    List<TextInputFormatter>? inputFormatters,
    bool obscureText = false,
    Widget? suffix,
  }) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Text(
        label,
        style: const TextStyle(
          color: Color(0xFF34453E),
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
      const SizedBox(height: 8),
      TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        textCapitalization: textCapitalization,
        autofillHints: autofillHints,
        inputFormatters: inputFormatters,
        obscureText: obscureText,
        validator: validator,
        decoration: InputDecoration(
          hintText: hint,
          suffixIcon: suffix,
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 15,
            horizontal: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(6),
            borderSide: const BorderSide(color: Color(0xFFD9DDD6)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(6),
            borderSide: const BorderSide(color: Color(0xFFD9DDD6)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(6),
            borderSide: const BorderSide(color: Color(0xFFB86B43), width: 1.5),
          ),
          errorMaxLines: 2,
        ),
      ),
    ],
  );

  Widget _visibilityButton({
    required bool hidden,
    required VoidCallback onPressed,
    required String showTooltip,
    required String hideTooltip,
  }) => IconButton(
    tooltip: hidden ? showTooltip : hideTooltip,
    onPressed: onPressed,
    icon: Icon(
      hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined,
    ),
  );

  String? _requiredName(String? value) =>
      (value?.trim().isEmpty ?? true) ? 'Este campo es obligatorio.' : null;
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.message, required this.isError});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final foreground = isError
        ? const Color(0xFF84382C)
        : const Color(0xFF245A3F);
    final background = isError
        ? const Color(0xFFFFEFEB)
        : const Color(0xFFE9F4EB);
    final border = isError ? const Color(0xFFE9B6A8) : const Color(0xFFB5D7BD);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: background,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: foreground,
            size: 20,
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: foreground, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
