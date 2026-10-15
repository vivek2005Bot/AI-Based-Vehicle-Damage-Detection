import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../core/models/inspection_model.dart';
import '../../core/models/report_model.dart';
import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import 'widgets/image_overlay_viewer.dart';

class ReportScreen extends StatefulWidget {
  final String inspectionId;

  const ReportScreen({super.key, required this.inspectionId});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  InspectionReportModel? _report;
  InspectionModel? _inspection;
  bool _isLoading = true;
  String? _errorMessage;
  bool _isExporting = false;

  @override
  void initState() {
    super.initState();
    _fetchReport();
  }

  Future<void> _fetchReport() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        ApiClient.getReport(widget.inspectionId),
        ApiClient.getInspection(widget.inspectionId),
      ]);
      if (!mounted) return;
      setState(() {
        _report = results[0] as InspectionReportModel;
        _inspection = results[1] as InspectionModel;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  // --- Native iOS Share Sheet Export ---

  Future<void> _exportPdf() async {
    setState(() => _isExporting = true);
    try {
      final pdfBytes = await ApiClient.downloadPdf(widget.inspectionId);
      final tempDir = await getTemporaryDirectory();
      final filePath = '${tempDir.path}/inspection_report_${widget.inspectionId.substring(0, 8)}.pdf';
      final file = File(filePath);
      await file.writeAsBytes(pdfBytes);

      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(filePath, mimeType: 'application/pdf')],
          text: 'Vehicle Damage AI Inspection Report',
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Export PDF failed: $e')),
      );
    } finally {
      if (mounted) setState(() => _isExporting = false);
    }
  }

  Future<void> _exportJson() async {
    if (_report == null) return;
    try {
      final tempDir = await getTemporaryDirectory();
      final filePath = '${tempDir.path}/inspection_report_${widget.inspectionId.substring(0, 8)}.json';
      final file = File(filePath);
      await file.writeAsString(jsonEncode({
        'inspection_id': _report!.inspectionId,
        'generated_at': _report!.generatedAt,
        'risk_class': _report!.riskClass,
        'risk_summary': _report!.riskSummary,
        'damage_detected': _report!.damageDetected,
        'assessment': _report!.assessment,
        'assessment_reason': _report!.assessmentReason,
        'severity_score': _report!.severityScore,
        'severity_level': _report!.severityLevel,
        'disclaimer': _report!.disclaimer,
      }));

      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(filePath, mimeType: 'application/json')],
          text: 'Vehicle Damage AI JSON Report',
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Export JSON failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspection Findings & Report'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            tooltip: 'Export / Share',
            onPressed: _report == null ? null : _showExportSheet,
          ),
        ],
      ),
      body: Column(
        children: [
          if (_isExporting) const LinearProgressIndicator(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _errorMessage != null
                    ? _buildErrorView()
                    : _buildReportContent(),
          ),
        ],
      ),
    );
  }

  void _showExportSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Export Inspection Report',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.picture_as_pdf_rounded, color: Colors.redAccent),
                  title: const Text('Download & Share PDF Report'),
                  subtitle: const Text('Printable document with findings, charts, and citations'),
                  onTap: () {
                    Navigator.pop(context);
                    _exportPdf();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.code_rounded, color: AppTheme.primaryCobalt),
                  title: const Text('Export JSON Data Payload'),
                  subtitle: const Text('Machine-readable telemetry & computer vision coordinates'),
                  onTap: () {
                    Navigator.pop(context);
                    _exportJson();
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 52, color: AppTheme.unsafeRed),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _fetchReport,
              child: const Text('Retry Loading Report'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReportContent() {
    final report = _report!;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 1. Risk Banner
          _buildRiskBanner(report),
          const SizedBox(height: 16),

          // 2. Executive Damage Summary Card
          _buildSeverityCard(report),
          const SizedBox(height: 20),

          // 3. Visual Findings with Bounding Box & Polygon Overlays
          const Text(
            'Exterior Visual Findings',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          if (report.images.isEmpty)
            const Text('No images were processed.', style: TextStyle(color: AppTheme.textMuted))
          else
            ...report.images.map((finding) => Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: ImageOverlayViewer(
                      inspectionId: widget.inspectionId,
                      finding: finding,
                      inspectionFiles: _inspection?.files ?? const []),
                )),

          const SizedBox(height: 20),

          // 4. OBD-II Telemetry Findings
          const Text(
            'OBD-II Telemetry & DTC Findings',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          _buildObdCard(report),

          const SizedBox(height: 20),

          // 5. Grounded RAG Guidance
          const Text(
            'Grounded Safety & Repair Guidance',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          _buildGuidanceCard(report),

          const SizedBox(height: 24),

          // 6. Mandatory Safety Disclaimer
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceLight,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.borderSubtle),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, size: 18, color: AppTheme.textMuted),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    report.disclaimer,
                    style: const TextStyle(fontSize: 11, color: AppTheme.textMuted, height: 1.4, fontStyle: FontStyle.italic),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildRiskBanner(InspectionReportModel report) {
    Color bg = AppTheme.safeGreen;
    Color fg = Colors.white;
    IconData icon = Icons.check_circle_rounded;
    String label = 'SAFE FOR TYPICAL CONDITIONS';

    final rc = report.riskClass.toLowerCase();
    final visionInconclusive = report.assessment == 'inconclusive';
    if (rc == 'caution') {
      bg = AppTheme.cautionAmber;
      icon = Icons.warning_amber_rounded;
      label = 'CAUTION — ADVISORY ISSUES OBSERVED';
    } else if (rc == 'unsafe') {
      bg = AppTheme.unsafeRed;
      icon = Icons.dangerous_rounded;
      label = 'UNSAFE — CRITICAL RISKS DETECTED';
    } else if (rc == 'unavailable' || visionInconclusive) {
      // Never render the default green SAFE banner for an inconclusive assessment.
      bg = const Color(0xFF64748B);
      icon = Icons.help_outline_rounded;
      label = 'UNABLE TO DETERMINE — MANUAL REVIEW REQUIRED';
    }

    return Container(
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: bg.withValues(alpha: 0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: fg, size: 26),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  label,
                  style: TextStyle(color: fg, fontWeight: FontWeight.w800, fontSize: 14, letterSpacing: -0.2),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            report.riskSummary,
            style: TextStyle(color: fg.withValues(alpha: 0.95), fontSize: 13, height: 1.35),
          ),
          if (report.reviewRequired) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.18),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Professional qualified inspection recommended',
                style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSeverityCard(InspectionReportModel report) {
    final isInconclusive = report.assessment == 'inconclusive';
    final isDamaged = report.assessment == 'damaged' || report.damageDetected;
    final damageLabel = isDamaged ? 'YES' : (isInconclusive ? 'UNKNOWN' : 'NO');
    final damageColor = isDamaged
        ? AppTheme.unsafeRed
        : (isInconclusive ? AppTheme.cautionAmber : AppTheme.safeGreen);
    final scoreStr = report.severityScore != null
        ? (report.severityScore! * 100).toStringAsFixed(1)
        : '—';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Damage Detected', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text(
                      damageLabel,
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                        color: damageColor,
                      ),
                    ),
                  ],
                ),
                Container(height: 36, width: 1, color: AppTheme.borderSubtle),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Severity Level', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text(
                      report.severityLevel == 'unavailable' && isInconclusive
                          ? 'N/A'
                          : report.severityLevel.toUpperCase(),
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.primaryDark),
                    ),
                  ],
                ),
                Container(height: 36, width: 1, color: AppTheme.borderSubtle),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Severity Score', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text(
                      '$scoreStr / 100',
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.primaryCobalt),
                    ),
                  ],
                ),
              ],
            ),
            if (isInconclusive) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.cautionAmber.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.cautionAmber.withValues(alpha: 0.4)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.help_outline_rounded, size: 16, color: AppTheme.cautionAmber),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Unable to determine — manual review required.'
                        '${report.assessmentReason != null && report.assessmentReason!.isNotEmpty ? ' ${report.assessmentReason}' : ''}',
                        style: const TextStyle(fontSize: 12, color: AppTheme.textMain, height: 1.35),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildObdCard(InspectionReportModel report) {
    if (report.obdStatus == 'not_provided') {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: const [
              Icon(Icons.info_outline, color: AppTheme.textMuted, size: 24),
              SizedBox(width: 12),
              Expanded(
                child: Text(
                  'No OBD-II telemetry log was uploaded with this inspection. Powertrain and electronic subsystem health was not evaluated.',
                  style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Telemetry Status', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: (report.obdAnomalyDetected ?? false) ? AppTheme.unsafeRed.withValues(alpha: 0.12) : AppTheme.safeGreen.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    (report.obdAnomalyDetected ?? false) ? 'ANOMALIES DETECTED' : 'NORMAL READINGS',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: (report.obdAnomalyDetected ?? false) ? AppTheme.unsafeRed : AppTheme.safeGreen,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(color: AppTheme.borderSubtle, height: 20),

            // DTCs
            if (report.dtcs.isNotEmpty) ...[
              const Text('Active Diagnostic Trouble Codes (DTCs):', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppTheme.textMuted)),
              const SizedBox(height: 6),
              ...report.dtcs.map((dtc) => Container(
                    margin: const EdgeInsets.only(bottom: 6),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceLight,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.borderSubtle),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: AppTheme.unsafeRed, borderRadius: BorderRadius.circular(4)),
                          child: Text(dtc.code, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 11)),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(dtc.description, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
                        ),
                      ],
                    ),
                  )),
            ],

            // Flagged PIDs
            if (report.flaggedPids.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text('Flagged Telemetry PIDs:', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppTheme.textMuted)),
              const SizedBox(height: 6),
              ...report.flaggedPids.map((pid) => Text(
                    '• ${pid.pidName}: ${pid.observedValue} ${pid.unit} — ${pid.reason}',
                    style: const TextStyle(fontSize: 12, color: AppTheme.textMain, height: 1.3),
                  )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildGuidanceCard(InspectionReportModel report) {
    if (report.guidance.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            'No verified repair guidance was found in the configured knowledge base.',
            style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
        ),
      );
    }

    return Column(
      children: report.guidance.map((passage) {
        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  passage.content,
                  style: const TextStyle(fontSize: 13, height: 1.4, color: AppTheme.textMain),
                ),
                const SizedBox(height: 8),
                Text(
                  'Citation: ${passage.documentTitle} (${passage.publisher}), ${passage.section}',
                  style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.textMuted),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}
