import 'package:flutter/material.dart';
import '../../core/config/api_config.dart';
import '../../core/theme/app_theme.dart';
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

  Future<void> _saveBaseUrl() async {
    setState(() => _isSaving = true);
    final url = _urlController.text.trim();
    if (url.isNotEmpty) {
      await ApiConfig.setBaseUrl(url);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Backend URL updated successfully'),
            backgroundColor: AppTheme.safeGreen,
          ),
        );
      }
    }
    setState(() => _isSaving = false);
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Log Out'),
        content: const Text('Are you sure you want to log out of this device? Local authentication tokens will be removed.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.unsafeRed),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Log Out', style: TextStyle(color: Colors.white)),
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Compliance'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Section: Backend Configuration
          const Text(
            'BACKEND CONNECTION',
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
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'API Server Base URL',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Configure host for local development (e.g., http://localhost:8000 or your LAN IP)',
                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
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
                      onPressed: _isSaving ? null : _saveBaseUrl,
                      icon: _isSaving
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.save_rounded, size: 18),
                      label: const Text('Save Endpoint'),
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
          const Text(
            'SESSION MANAGEMENT',
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
            child: ListTile(
              leading: const Icon(Icons.logout_rounded, color: AppTheme.unsafeRed),
              title: const Text('Sign Out', style: TextStyle(color: AppTheme.unsafeRed, fontWeight: FontWeight.bold)),
              subtitle: const Text('End current session and clear local security tokens'),
              onTap: _handleLogout,
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
