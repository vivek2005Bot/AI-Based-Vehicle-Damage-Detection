import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../core/models/inspection_model.dart';
import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import '../history/history_screen.dart';
import '../new_inspection/new_inspection_screen.dart';
import '../progress/analysis_progress_screen.dart';
import '../report/report_screen.dart';
import '../settings/settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<InspectionModel> _recentInspections = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final list = await ApiClient.listInspections();
      if (!mounted) return;
      setState(() {
        _recentInspections = list;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _onInspectionTap(InspectionModel item) {
    if (item.status == 'completed' ||
        item.status == 'completed_with_warnings') {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ReportScreen(inspectionId: item.id)),
      ).then((_) => _loadData());
    } else if (item.status == 'queued' || item.status == 'processing') {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => AnalysisProgressScreen(inspectionId: item.id),
        ),
      ).then((_) => _loadData());
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Inspection status: ${item.status}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vehicle Damage AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history_rounded),
            tooltip: 'All Inspections',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const HistoryScreen()),
              ).then((_) => _loadData());
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Settings',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Hero Start Action Card
              Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E3A8A), Color(0xFF2563EB)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF2563EB).withValues(alpha: 0.35),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(22.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.18),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'Multimodal AI Diagnostic',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        const Icon(
                          Icons.auto_awesome,
                          color: AppTheme.accentCyan,
                          size: 22,
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Automated Vehicle\nDamage Inspection',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w700,
                        height: 1.2,
                        letterSpacing: -0.4,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Capture exterior photos and optional OBD-II telemetry logs for grounded risk assessment.',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.85),
                        fontSize: 13,
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const NewInspectionScreen(),
                          ),
                        ).then((_) => _loadData());
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppTheme.primaryDark,
                        minimumSize: const Size.fromHeight(48),
                        elevation: 0,
                      ),
                      icon: const Icon(
                        Icons.add_photo_alternate_rounded,
                        size: 20,
                      ),
                      label: const Text(
                        'Start New Inspection',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Pipeline Features Overview
              const Text(
                'AI Inspection Capabilities',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.primaryDark,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _buildPill(Icons.filter_alt_outlined, 'Stage 1 Filter'),
                  const SizedBox(width: 8),
                  _buildPill(Icons.crop_free, 'Object Detection'),
                  const SizedBox(width: 8),
                  _buildPill(Icons.speed, 'OBD Anomaly'),
                  const SizedBox(width: 8),
                  _buildPill(Icons.menu_book, 'RAG Standards'),
                ],
              ),

              const SizedBox(height: 28),

              // Recent Inspections Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Recent Inspections',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.primaryDark,
                    ),
                  ),
                  if (_recentInspections.isNotEmpty)
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const HistoryScreen(),
                          ),
                        ).then((_) => _loadData());
                      },
                      child: const Text(
                        'View All',
                        style: TextStyle(fontSize: 13),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 10),

              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 40.0),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceLight,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.cloud_off_rounded,
                        color: AppTheme.textMuted,
                        size: 36,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Error connecting: $_error',
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppTheme.textMuted,
                        ),
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: _loadData,
                        child: const Text('Retry Connection'),
                      ),
                    ],
                  ),
                )
              else if (_recentInspections.isEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(
                    vertical: 36,
                    horizontal: 20,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.borderSubtle),
                  ),
                  child: Column(
                    children: [
                      Icon(
                        Icons.directions_car_outlined,
                        size: 48,
                        color: AppTheme.textMuted.withValues(alpha: 0.5),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'No inspections yet',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: AppTheme.primaryDark,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Tap "Start New Inspection" above to photograph a vehicle and run the AI assessment.',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: AppTheme.textMuted,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                )
              else
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _recentInspections.take(5).length,
                  separatorBuilder: (_, _) => const SizedBox(height: 10),
                  itemBuilder: (context, index) {
                    final item = _recentInspections[index];
                    return _buildInspectionCard(item);
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPill(IconData icon, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.borderSubtle),
        ),
        child: Column(
          children: [
            Icon(icon, size: 20, color: AppTheme.primaryCobalt),
            const SizedBox(height: 4),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppTheme.textMain,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInspectionCard(InspectionModel item) {
    Color badgeColor = Colors.grey;
    String badgeText = item.status.toUpperCase();

    if (item.riskClass != null) {
      final rc = item.riskClass!.toLowerCase();
      if (rc == 'safe') {
        badgeColor = AppTheme.safeGreen;
        badgeText = 'SAFE';
      } else if (rc == 'caution') {
        badgeColor = AppTheme.cautionAmber;
        badgeText = 'CAUTION';
      } else if (rc == 'unsafe') {
        badgeColor = AppTheme.unsafeRed;
        badgeText = 'UNSAFE';
      } else if (rc == 'unavailable') {
        badgeColor = Colors.grey.shade600;
        badgeText = 'REVIEW NEEDED';
      }
    } else if (item.status == 'queued' || item.status == 'processing') {
      badgeColor = AppTheme.accentCyan;
      badgeText = 'PROCESSING';
    }

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        onTap: () => _onInspectionTap(item),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: badgeColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(Icons.directions_car, color: badgeColor, size: 24),
        ),
        title: Text(
          item.vehicleDisplayName,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
        ),
        subtitle: Text(
          '${DateFormat('MMM d, yyyy • HH:mm').format(item.createdAt.toLocal())} • ${item.files.length} file(s)',
          style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: badgeColor.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: badgeColor.withValues(alpha: 0.3)),
          ),
          child: Text(
            badgeText,
            style: TextStyle(
              color: badgeColor,
              fontWeight: FontWeight.w700,
              fontSize: 11,
            ),
          ),
        ),
      ),
    );
  }
}
