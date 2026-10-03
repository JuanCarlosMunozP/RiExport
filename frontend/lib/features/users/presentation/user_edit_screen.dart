import 'package:flutter/material.dart';

import '../../../core/api/api_exception.dart';

class UserEditScreen extends StatefulWidget {
  const UserEditScreen({super.key, required this.user, required this.onSave});

  final Map<String, dynamic> user;
  final Future<void> Function(Map<String, Object?> changes) onSave;

  @override
  State<UserEditScreen> createState() => _UserEditScreenState();
}

class _UserEditScreenState extends State<UserEditScreen> {
  final _formKey = GlobalKey<FormState>();
  late final _firstName = TextEditingController(
    text: '${widget.user['first_name'] ?? ''}',
  );
  late final _lastName = TextEditingController(
    text: '${widget.user['last_name'] ?? ''}',
  );
  late final _email = TextEditingController(
    text: '${widget.user['email'] ?? ''}',
  );
  late final _phone = TextEditingController(
    text: '${widget.user['phone'] ?? ''}',
  );
  late final _roleId = TextEditingController(
    text: '${widget.user['role_id'] ?? ''}',
  );
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _email.dispose();
    _phone.dispose();
    _roleId.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    if (!_formKey.currentState!.validate()) return;
    final changes =
        <String, Object?>{
          'first_name': _firstName.text.trim(),
          'last_name': _lastName.text.trim(),
          'email': _email.text.trim(),
          'phone': _phone.text.trim().isEmpty ? null : _phone.text.trim(),
          'role_id': int.parse(_roleId.text),
        }..removeWhere(
          (key, value) =>
              value == widget.user[key] ||
              (key == 'phone' && value == (widget.user[key] ?? '')),
        );
    if (changes.isEmpty) {
      Navigator.of(context).pop(false);
      return;
    }

    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await widget.onSave(changes);
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (exception) {
      if (mounted) {
        setState(() {
          _error = exception.message;
          _saving = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _error = 'No fue posible guardar los cambios.';
          _saving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xFFF6F5F0),
    appBar: AppBar(
      title: const Text('Editar usuario'),
      backgroundColor: const Color(0xFFF6F5F0),
      leading: IconButton(
        tooltip: 'Volver al listado',
        onPressed: _saving ? null : () => Navigator.of(context).pop(false),
        icon: const Icon(Icons.arrow_back_rounded),
      ),
    ),
    body: SafeArea(
      top: false,
      child: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 36),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 680),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      '${widget.user['first_name'] ?? ''} ${widget.user['last_name'] ?? ''}'
                          .trim(),
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(
                            color: const Color(0xFF193D35),
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'ID ${widget.user['id'] ?? '—'}',
                      style: const TextStyle(color: Color(0xFF68736E)),
                    ),
                    const SizedBox(height: 26),
                    _field(
                      _firstName,
                      'Nombres',
                      validator: _required,
                      textCapitalization: TextCapitalization.words,
                    ),
                    const SizedBox(height: 18),
                    _field(
                      _lastName,
                      'Apellidos',
                      validator: _required,
                      textCapitalization: TextCapitalization.words,
                    ),
                    const SizedBox(height: 18),
                    _field(
                      _email,
                      'Correo electrónico',
                      keyboardType: TextInputType.emailAddress,
                      validator: _validateEmail,
                    ),
                    const SizedBox(height: 18),
                    _field(
                      _phone,
                      'Teléfono (opcional)',
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 18),
                    _field(
                      _roleId,
                      'ID del rol',
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        final id = int.tryParse(value?.trim() ?? '');
                        return id == null || id < 1
                            ? 'Ingresa un ID de rol válido.'
                            : null;
                      },
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 18),
                      _ErrorBanner(message: _error!),
                    ],
                    if (_saving) ...[
                      const SizedBox(height: 18),
                      const LinearProgressIndicator(minHeight: 2),
                    ],
                    const SizedBox(height: 28),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: _saving
                                ? null
                                : () => Navigator.of(context).pop(false),
                            child: const Text('Cancelar'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: _saving ? null : _submit,
                            icon: const Icon(Icons.save_outlined),
                            label: Text(_saving ? 'Guardando…' : 'Guardar'),
                            style: FilledButton.styleFrom(
                              backgroundColor: const Color(0xFF193D35),
                            ),
                          ),
                        ),
                      ],
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

  Widget _field(
    TextEditingController controller,
    String label, {
    String? Function(String?)? validator,
    TextInputType? keyboardType,
    TextCapitalization textCapitalization = TextCapitalization.none,
  }) => TextFormField(
    controller: controller,
    keyboardType: keyboardType,
    textCapitalization: textCapitalization,
    validator: validator,
    decoration: InputDecoration(
      labelText: label,
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(6)),
    ),
  );

  String? _required(String? value) =>
      value?.trim().isNotEmpty == true ? null : 'Este campo es obligatorio.';

  String? _validateEmail(String? value) {
    if (_required(value) != null) return 'Ingresa el correo electrónico.';
    return RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(value!.trim())
        ? null
        : 'Ingresa un correo válido.';
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: const Color(0xFFFFEFEB),
      border: Border.all(color: const Color(0xFFE9B6A8)),
      borderRadius: BorderRadius.circular(6),
    ),
    child: Text(message, style: const TextStyle(color: Color(0xFF84382C))),
  );
}
