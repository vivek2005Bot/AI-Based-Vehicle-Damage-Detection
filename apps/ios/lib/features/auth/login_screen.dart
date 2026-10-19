import 'package:flutter/material.dart';
import '../../core/config/api_config.dart';
import '../../core/localization/language_selector_widget.dart';
import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import '../../l10n/generated/app_localizations.dart';
import '../home/home_screen.dart';
import '../settings/settings_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController(text: 'inspector@example.com');
  final _passwordController = TextEditingController(text: 'securePassword123!');
  bool _isRegisterMode = false;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit(AppLocalizations? l10n) async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      setState(() => _errorMessage = l10n?.emailRequired ?? 'Please enter both email and password.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      if (_isRegisterMode) {
        await ApiClient.register(email, password);
      }
      await ApiClient.login(email, password);

      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(_isRegisterMode ? (l10n?.createAccount ?? 'Create Account') : (l10n?.signIn ?? 'Sign In')),
        actions: [
          const LanguageSelectorWidget(compact: true),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: l10n?.settings ?? 'Server Settings',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                _isRegisterMode
                    ? (l10n?.createAccount ?? 'Register Inspector Account')
                    : (l10n?.welcomeBack ?? 'Welcome Back'),
                style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.primaryDark,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _isRegisterMode
                    ? (l10n?.registerSubtitle ?? 'Register an inspector account to start vehicle roadworthiness assessments.')
                    : (l10n?.loginSubtitle ?? 'Sign in to capture inspections, upload telemetry, and generate grounded safety reports.'),
                style: const TextStyle(fontSize: 14, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 28),
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.unsafeRed.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppTheme.unsafeRed.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: AppTheme.unsafeRed, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: AppTheme.unsafeRed, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],
              TextField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                autocorrect: false,
                decoration: InputDecoration(
                  labelText: l10n?.emailLabel ?? 'Email Address',
                  hintText: l10n?.emailHint ?? 'inspector@example.com',
                  prefixIcon: const Icon(Icons.email_outlined, color: AppTheme.textMuted),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: l10n?.passwordLabel ?? 'Password',
                  hintText: l10n?.passwordHint ?? '••••••••••••',
                  prefixIcon: const Icon(Icons.lock_outline, color: AppTheme.textMuted),
                ),
              ),
              const SizedBox(height: 28),
              ElevatedButton(
                onPressed: _isLoading ? null : () => _submit(l10n),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : Text(_isRegisterMode ? (l10n?.createAccount ?? 'Register') : (l10n?.signInButton ?? 'Sign In')),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  setState(() {
                    _isRegisterMode = !_isRegisterMode;
                    _errorMessage = null;
                  });
                },
                child: Text(
                  _isRegisterMode
                      ? (l10n?.alreadyHaveAccount ?? 'Already have an account? Sign In')
                      : (l10n?.needAccount ?? 'Don\'t have an account? Create One'),
                  style: const TextStyle(color: AppTheme.primaryCobalt, fontWeight: FontWeight.w600),
                ),
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceLight,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, size: 18, color: AppTheme.textMuted),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Connected API: ${ApiConfig.currentBaseUrl}',
                        style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
