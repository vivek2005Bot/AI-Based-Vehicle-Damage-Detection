import 'package:flutter/material.dart';
import '../../core/config/api_config.dart';
import '../../core/localization/language_selector_widget.dart';
import '../../core/theme/app_theme.dart';
import '../../l10n/generated/app_localizations.dart';
import '../auth/login_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _urlController.text = ApiConfig.currentBaseUrl;
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _saveBaseUrl(AppLocalizations? l10n) async {
    setState(() => _isSaving = true);
    final url = _urlController.text.trim();
    if (url.isNotEmpty) {
      await ApiConfig.setBaseUrl(url);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n?.backendUrlUpdated ?? 'Backend URL updated successfully'),
            backgroundColor: AppTheme.safeGreen,
          ),
        );
      }
    }
    setState(() => _isSaving = false);
  }

  Future<void> _handleLogout(AppLocalizations? l10n) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n?.signOut ?? 'Log Out'),
        content: Text(l10n?.logoutConfirmation ?? 'Are you sure you want to log out of this device? Local authentication tokens will be removed.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n?.cancel ?? 'Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.unsafeRed),
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(l10n?.signOut ?? 'Log Out', style: const TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await ApiConfig.setToken(null);
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const LoginScreen()),
          (route) => false,
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.settingsAndCompliance ?? 'Settings & Compliance'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Section: Language & Locale
          Text(
            l10n?.languageSectionHeader ?? 'APPLICATION LANGUAGE / भाषा',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.1,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.translate, color: AppTheme.primaryCobalt, size: 22),
                      const SizedBox(width: 10),
                      Text(
                        l10n?.selectLanguage ?? 'Preferred Language',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    l10n?.languageSettingSubtitle ??
                        'Select from English or any of the 22 Scheduled Languages of India. Updates the entire application immediately.',
                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 12),
                  const LanguageSelectorWidget(),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Section: Backend Configuration
          Text(
            l10n?.backendConnection ?? 'BACKEND CONNECTION',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.1,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n?.apiServerUrl ?? 'API Server Base URL',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    l10n?.apiServerUrlSubtitle ?? 'Configure host for local development (e.g., http://localhost:8000 or your LAN IP)',
                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _urlController,
                    decoration: const InputDecoration(
                      prefixIcon: Icon(Icons.dns_rounded),
                      hintText: 'http://localhost:8000',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Align(
                    alignment: Alignment.centerRight,
                    child: ElevatedButton.icon(
                      onPressed: _isSaving ? null : () => _saveBaseUrl(l10n),
                      icon: _isSaving
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.save_rounded, size: 18),
                      label: Text(l10n?.saveEndpoint ?? 'Save Endpoint'),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Section: Privacy & Security Disclaimers
          const Text(
            'PRIVACY & LEGAL NOTICES',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.1,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.shield_outlined, color: AppTheme.primaryDark),
                  title: const Text('Vehicle Identification Privacy'),
                  subtitle: const Text('License plates and human faces are automatically blurred prior to cloud analysis.'),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Privacy Safeguards'),
                        content: const Text(
                          'In adherence to automotive privacy standards and data protection regulations, '
                          'captured inspection photos undergo client-side and server-side anonymization.\n\n'
                          'License plates and identifiable passenger faces are blurred or masked before '
                          'model training or permanent storage.',
                        ),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Dismiss')),
                        ],
                      ),
                    );
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.warning_amber_rounded, color: AppTheme.cautionAmber),
                  title: const Text('Decision-Support Disclaimer'),
                  subtitle: const Text('AI assessments assist human inspectors and do not replace physical roadworthiness inspections.'),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Decision-Support Advisory'),
                        content: const Text(
                          'Roadworthiness assessments (Safe, Caution, Unsafe) generated by this system '
                          'are automated recommendations intended exclusively to support trained human examiners.\n\n'
                          'This application does not issue a legally binding guarantee of structural integrity '
                          'or roadworthiness. Critical vehicle safety systems (braking, airbag SRS, suspension geometry) '
                          'must always be inspected physically by a certified mechanic.',
                        ),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Understood')),
                        ],
                      ),
                    );
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.menu_book_rounded, color: AppTheme.primaryCobalt),
                  title: const Text('Regulatory Knowledge Base'),
                  subtitle: const Text('Grounding based on NHTSA, AGRSS/ANSI, USTMA, and SAE J2012 standards.'),
                  onTap: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Regulatory Grounding'),
                        content: const Text(
                          'Our RAG retrieval agent indexes authoritative documents:\n\n'
                          '• NHTSA FMVSS 208 / 214: Structural crashworthiness\n'
                          '• AGRSS / ANSI 003: Windshield replacement standards\n'
                          '• USTMA Tire Replacement Guidelines: Sidewall damage\n'
                          '• SAE J2012 / ISO 15031: Diagnostic Trouble Codes (DTC)',
                        ),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Section: Account Actions
          Text(
            l10n?.sessionManagement ?? 'SESSION MANAGEMENT',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.1,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: const Icon(Icons.logout_rounded, color: AppTheme.unsafeRed),
              title: Text(l10n?.signOut ?? 'Sign Out', style: const TextStyle(color: AppTheme.unsafeRed, fontWeight: FontWeight.bold)),
              subtitle: Text(l10n?.signOutSubtitle ?? 'End current session and clear local security tokens'),
              onTap: () => _handleLogout(l10n),
            ),
          ),
          const SizedBox(height: 40),
          const Center(
            child: Text(
              'Automotive Inspection AI v1.0.0\nBuilt to ANTIGRAVITY_PROJECT_SPEC standards',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
            ),
          ),
        ],
      ),
    );
  }
}
