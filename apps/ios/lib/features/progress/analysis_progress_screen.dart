import 'dart:async';
import 'package:flutter/material.dart';

import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import '../report/report_screen.dart';

class AnalysisProgressScreen extends StatefulWidget {
  final String inspectionId;

  const AnalysisProgressScreen({super.key, required this.inspectionId});

  @override
  State<AnalysisProgressScreen> createState() => _AnalysisProgressScreenState();
}

class _AnalysisProgressScreenState extends State<AnalysisProgressScreen> {
  Timer? _pollTimer;
  String _status = 'queued';
  String _currentStage = 'queued';
  String? _errorMessage;
  int _pollCount = 0;

  final List<Map<String, dynamic>> _stages = [
    {'id': 'input_validation', 'title': 'Input Validation & Preprocessing', 'icon': Icons.tune_rounded},
    {'id': 'vision_analysis', 'title': '4-Stage Vision Cascade (Filter, Detect, Segment)', 'icon': Icons.visibility_rounded},
    {'id': 'obd_analysis', 'title': 'OBD-II Telemetry & DTC Anomaly Detection', 'icon': Icons.speed_rounded},
    {'id': 'knowledge_retrieval', 'title': 'RAG Knowledge Standards Retrieval', 'icon': Icons.menu_book_rounded},
    {'id': 'report_generation', 'title': 'Risk Engine & Report Generation', 'icon': Icons.assessment_rounded},
  ];

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _pollTimer = Timer.periodic(const Duration(seconds: 2), (_) => _checkStatus());
    _checkStatus();
  }

  Future<void> _checkStatus() async {
    _pollCount++;
    try {
      final data = await ApiClient.getStatus(widget.inspectionId);
      final status = (data['status'] as String? ?? '').toLowerCase();
      final stage = (data['current_stage'] as String? ?? '').toLowerCase();

      if (!mounted) return;
      setState(() {
        _status = status;
        _currentStage = stage;
      });

      if (status == 'completed' || status == 'completed_with_warnings') {
        _pollTimer?.cancel();
        await Future.delayed(const Duration(milliseconds: 500));
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ReportScreen(inspectionId: widget.inspectionId),
          ),
        );
      } else if (status == 'failed') {
        _pollTimer?.cancel();
        setState(() {
          _errorMessage = 'Analysis pipeline failed on server. Please check inputs and retry.';
        });
      }
    } catch (e) {
      if (_pollCount > 10) {
        setState(() => _errorMessage = 'Unable to reach backend server: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Processing Inspection'),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 12),
              Center(
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryCobalt.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: SizedBox(
                      width: 36,
                      height: 36,
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        color: AppTheme.primaryCobalt,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'AI Multi-Agent Pipeline Running',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.primaryDark,
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Our LangGraph supervisor is coordinating specialist agents across vision, telemetry, and safety standards.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
              ),
              const SizedBox(height: 32),

              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppTheme.unsafeRed.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.unsafeRed.withValues(alpha: 0.3)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.error_outline, color: AppTheme.unsafeRed),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _errorMessage!,
                              style: const TextStyle(color: AppTheme.unsafeRed, fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('Back to Home'),
                      ),
                    ],
                  ),
                ),
              ] else ...[
                Expanded(
                  child: ListView.separated(
                    itemCount: _stages.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 14),
                    itemBuilder: (context, index) {
                      final stage = _stages[index];
                      return _buildStageTile(stage, index);
                    },
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStageTile(Map<String, dynamic> stage, int index) {
    final stageId = stage['id'] as String;
    final isCurrent = _currentStage.contains(stageId.split('_').first);
    final isCompleted = _status == 'completed' || _status == 'completed_with_warnings';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: isCurrent ? AppTheme.primaryCobalt.withValues(alpha: 0.06) : AppTheme.surfaceLight,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isCurrent ? AppTheme.primaryCobalt : AppTheme.borderSubtle,
          width: isCurrent ? 1.5 : 1.0,
        ),
      ),
      child: Row(
        children: [
          Icon(
            stage['icon'] as IconData,
            color: isCurrent ? AppTheme.primaryCobalt : AppTheme.textMuted,
            size: 22,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              stage['title'] as String,
              style: TextStyle(
                fontSize: 13,
                fontWeight: isCurrent ? FontWeight.w700 : FontWeight.w500,
                color: isCurrent ? AppTheme.primaryCobalt : AppTheme.textMain,
              ),
            ),
          ),
          if (isCurrent && !isCompleted)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primaryCobalt),
            )
          else if (isCompleted)
            const Icon(Icons.check_circle_rounded, color: AppTheme.safeGreen, size: 20)
          else
            const Icon(Icons.schedule, color: AppTheme.textMuted, size: 18),
        ],
      ),
    );
  }
}
