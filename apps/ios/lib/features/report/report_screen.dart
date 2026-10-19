import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../core/models/inspection_model.dart';
import '../../core/models/report_model.dart';
import '../../core/networking/api_client.dart';
import '../../core/localization/diagnostic_localization.dart';
import '../../core/localization/language_selector_widget.dart';
import '../../core/localization/locale_service.dart';
import '../../core/theme/app_theme.dart';
import '../../l10n/generated/app_localizations.dart';
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
  int _selectedScenarioTab = 0;
  bool _isUpdatingEstimate = false;
  RepairEstimateModel? _customEstimate;

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
      final rep = results[0] as InspectionReportModel;
      setState(() {
        _report = rep;
        _inspection = results[1] as InspectionModel;
        _customEstimate = rep.estimate;
        if (rep.estimate != null) {
          _selectedScenarioTab = rep.estimate!.repairScenario.isRecommended ? 0 : 1;
        }
        _isLoading = false;
      });

      // If estimate is missing, fetch or generate it on-the-fly
      if (rep.estimate == null) {
        try {
          final est = await ApiClient.getEstimate(widget.inspectionId);
          if (mounted) {
            setState(() {
              _customEstimate = est;
              _selectedScenarioTab = est.repairScenario.isRecommended ? 0 : 1;
            });
          }
        } catch (_) {
          try {
            final est = await ApiClient.updateEstimate(widget.inspectionId);
            if (mounted) {
              setState(() {
                _customEstimate = est;
                _selectedScenarioTab = est.repairScenario.isRecommended ? 0 : 1;
              });
            }
          } catch (_) {}
        }
      }
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
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n?.inspectionFindingsReport ?? 'Inspection Findings & Report'),
        actions: [
          const LanguageSelectorWidget(compact: true),
          IconButton(
            icon: const Icon(Icons.share_outlined),
            tooltip: l10n?.exportInspectionReport ?? 'Export / Share',
            onPressed: _report == null ? null : () => _showExportSheet(l10n),
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
                    ? _buildErrorView(l10n)
                    : _buildReportContent(l10n),
          ),
        ],
      ),
    );
  }

  void _showExportSheet(AppLocalizations? l10n) {
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
                Text(
                  l10n?.exportInspectionReport ?? 'Export Inspection Report',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.picture_as_pdf_rounded, color: Colors.redAccent),
                  title: Text(l10n?.downloadPdfReport ?? 'Download & Share PDF Report'),
                  subtitle: Text(l10n?.downloadPdfSubtitle ?? 'Printable document with findings, charts, and citations'),
                  onTap: () {
                    Navigator.pop(context);
                    _exportPdf();
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.code_rounded, color: AppTheme.primaryCobalt),
                  title: Text(l10n?.exportJsonData ?? 'Export JSON Data Payload'),
                  subtitle: Text(l10n?.exportJsonSubtitle ?? 'Machine-readable telemetry & computer vision coordinates'),
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

  Widget _buildErrorView(AppLocalizations? l10n) {
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
              child: Text(l10n?.retryLoadingReport ?? 'Retry Loading Report'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReportContent(AppLocalizations? l10n) {
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
          Text(
            l10n?.exteriorVisualFindings ?? 'Exterior Visual Findings',
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          if (report.images.isEmpty)
            Text(l10n?.noImagesProcessed ?? 'No images were processed.', style: const TextStyle(color: AppTheme.textMuted))
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
          Text(
            l10n?.obdTelemetryFindings ?? 'OBD-II Telemetry & DTC Findings',
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          _buildObdCard(report),

          const SizedBox(height: 20),

          // 5. Grounded RAG Guidance
          Text(
            l10n?.groundedSafetyGuidance ?? 'Grounded Safety & Repair Guidance',
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 8),
          _buildGuidanceCard(report),

          const SizedBox(height: 20),

          // 5b. Vehicle Repair Cost Estimation
          _buildRepairCostEstimateCard(report),

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
    final langCode = LocaleService.currentLanguageCode;
    Color bg = AppTheme.safeGreen;
    Color fg = Colors.white;
    IconData icon = Icons.check_circle_rounded;

    final rc = report.riskClass.toLowerCase();
    final visionInconclusive = report.assessment == 'inconclusive';
    if (rc == 'caution') {
      bg = AppTheme.cautionAmber;
      icon = Icons.warning_amber_rounded;
    } else if (rc == 'unsafe') {
      bg = AppTheme.unsafeRed;
      icon = Icons.dangerous_rounded;
    } else if (rc == 'unavailable' || visionInconclusive) {
      // Never render the default green SAFE banner for an inconclusive assessment.
      bg = const Color(0xFF64748B);
      icon = Icons.help_outline_rounded;
    }

    final label = DiagnosticLocalization.getRiskBannerTitle(report.riskClass, visionInconclusive, langCode);
    final summary = DiagnosticLocalization.getRiskSummary(report.riskClass, report.riskSummary, langCode);

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
            summary,
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
              child: Text(
                DiagnosticLocalization.getProfessionalInspectionBadge(langCode),
                style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSeverityCard(InspectionReportModel report) {
    final langCode = LocaleService.currentLanguageCode;
    final isInconclusive = report.assessment == 'inconclusive';
    final isDamaged = report.assessment == 'damaged' || report.damageDetected;
    final damageLabel = DiagnosticLocalization.getBooleanLabel(
        isDamaged ? 'YES' : (isInconclusive ? 'UNKNOWN' : 'NO'), langCode);
    final damageColor = isDamaged
        ? AppTheme.unsafeRed
        : (isInconclusive ? AppTheme.cautionAmber : AppTheme.safeGreen);
    final scoreStr = report.severityScore != null
        ? (report.severityScore! * 100).toStringAsFixed(1)
        : '—';
    final severityLevelStr = report.severityLevel == 'unavailable' && isInconclusive
        ? 'N/A'
        : DiagnosticLocalization.getSeverityValue(report.severityLevel, langCode);

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
                    Text(DiagnosticLocalization.getDamageDetectedLabel(langCode),
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
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
                    Text(DiagnosticLocalization.getSeverityLevelLabel(langCode),
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text(
                      severityLevelStr,
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.primaryDark),
                    ),
                  ],
                ),
                Container(height: 36, width: 1, color: AppTheme.borderSubtle),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(DiagnosticLocalization.getSeverityScoreLabel(langCode),
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
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
                        '${DiagnosticLocalization.getInconclusiveBannerText(langCode)}'
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
    final langCode = LocaleService.currentLanguageCode;
    if (report.obdStatus == 'not_provided') {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              const Icon(Icons.info_outline, color: AppTheme.textMuted, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  DiagnosticLocalization.getNoObdTelemetryText(langCode),
                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final hasAnomalies = report.obdAnomalyDetected ?? false;
    final statusColor = hasAnomalies ? AppTheme.unsafeRed : AppTheme.safeGreen;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  DiagnosticLocalization.getTelemetryStatusLabel(langCode),
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    DiagnosticLocalization.getTelemetryStatusBadge(hasAnomalies, langCode),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: statusColor,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(color: AppTheme.borderSubtle, height: 20),

            // DTCs
            if (report.dtcs.isNotEmpty) ...[
              Text(
                DiagnosticLocalization.getActiveDtcsHeader(langCode),
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 8),
              ...report.dtcs.map((dtc) => _buildDtcItem(dtc)),
            ],

            // Flagged Telemetry Sensors
            if (report.flaggedPids.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                DiagnosticLocalization.getFlaggedSensorsHeader(langCode),
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: AppTheme.primaryDark),
              ),
              const SizedBox(height: 8),
              ...report.flaggedPids.map((pid) => _buildPidItem(pid)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDtcItem(DtcModel dtc) {
    final langCode = LocaleService.currentLanguageCode;
    Color urgencyColor;
    IconData urgencyIcon;
    final urg = dtc.urgency.toLowerCase();

    if (urg.contains('stop') || dtc.urgencyLabel.toLowerCase().contains('stop')) {
      urgencyColor = AppTheme.unsafeRed;
      urgencyIcon = Icons.dangerous_rounded;
    } else if (urg.contains('prompt') || dtc.urgencyLabel.toLowerCase().contains('prompt')) {
      urgencyColor = AppTheme.cautionAmber;
      urgencyIcon = Icons.warning_amber_rounded;
    } else if (urg.contains('schedule') || dtc.urgencyLabel.toLowerCase().contains('schedule')) {
      urgencyColor = AppTheme.primaryCobalt;
      urgencyIcon = Icons.schedule_rounded;
    } else {
      urgencyColor = AppTheme.textMuted;
      urgencyIcon = Icons.info_outline;
    }

    final dtcTitle = DiagnosticLocalization.getDtcTitle(dtc.code, dtc.simpleTitle, langCode);
    final urgencyText = DiagnosticLocalization.getUrgencyLabel(dtc.urgencyLabel, langCode);
    final whatItMeans = DiagnosticLocalization.getDtcWhatItMeans(dtc.code, dtc.whatItMeans, langCode);
    final whatYouShouldDo = DiagnosticLocalization.getDtcWhatYouShouldDo(dtc.code, dtc.whatYouShouldDo, langCode);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Code Badge + Title + Urgency Badge
          Wrap(
            spacing: 8,
            runSpacing: 6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.primaryDark,
                  borderRadius: BorderRadius.circular(5),
                ),
                child: Text(
                  dtc.code,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 11),
                ),
              ),
              Text(
                dtcTitle,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                decoration: BoxDecoration(
                  color: urgencyColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: urgencyColor.withValues(alpha: 0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(urgencyIcon, size: 12, color: urgencyColor),
                    const SizedBox(width: 4),
                    Text(
                      urgencyText,
                      style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.w700, color: urgencyColor),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // What it means (Plain language)
          Text(
            whatItMeans,
            style: const TextStyle(fontSize: 12.5, color: AppTheme.textMain, height: 1.35),
          ),
          const SizedBox(height: 8),

          // What you should do (Actionable Next Steps)
          if (whatYouShouldDo.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(9),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(7),
                border: Border.all(color: const Color(0xFFBBF7D0)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.assignment_turned_in_outlined, size: 15, color: Color(0xFF15803D)),
                  const SizedBox(width: 7),
                  Expanded(
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(fontSize: 11.5, color: Color(0xFF166534), height: 1.35),
                        children: [
                          TextSpan(
                            text: DiagnosticLocalization.getWhatYouShouldDoLabel(langCode),
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          TextSpan(text: whatYouShouldDo),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Expandable Technical Details & Symptoms
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              tilePadding: EdgeInsets.zero,
              childrenPadding: const EdgeInsets.only(top: 6, bottom: 4),
              title: Text(
                DiagnosticLocalization.getSymptomsCausesTitle(langCode),
                style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: AppTheme.primaryCobalt),
              ),
              children: [
                if (dtc.whatYouMightNotice.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      DiagnosticLocalization.getWhatYouMightNoticeLabel(langCode),
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                    ),
                  ),
                  const SizedBox(height: 3),
                  ...dtc.whatYouMightNotice.map((s) => Padding(
                        padding: const EdgeInsets.only(left: 6, bottom: 2),
                        child: Text('• $s', style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3)),
                      )),
                  const SizedBox(height: 6),
                ],
                if (dtc.whyItMatters.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3),
                        children: [
                          TextSpan(
                            text: DiagnosticLocalization.getWhyThisMattersLabel(langCode),
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          TextSpan(text: dtc.whyItMatters),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                ],
                if (dtc.possibleCauses.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      DiagnosticLocalization.getPossibleCausesLabel(langCode),
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                    ),
                  ),
                  const SizedBox(height: 3),
                  ...dtc.possibleCauses.map((c) => Padding(
                        padding: const EdgeInsets.only(left: 6, bottom: 2),
                        child: Text('• $c', style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3)),
                      )),
                  const SizedBox(height: 6),
                ],
                if (dtc.limitations.isNotEmpty) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF3C7),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: const Color(0xFFFDE68A)),
                    ),
                    child: Text(
                      '${DiagnosticLocalization.getNoticeLabel(langCode)}${dtc.limitations.join(' ')}',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), height: 1.3),
                    ),
                  ),
                  const SizedBox(height: 6),
                ],
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    '${DiagnosticLocalization.getStandardDefinitionLabel(langCode)}${dtc.description}\n${dtc.technicalDetails}',
                    style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.textMuted, height: 1.35),
                  ),
                ),
                const SizedBox(height: 4),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    '${DiagnosticLocalization.getVerifiedSourceLabel(langCode)}${dtc.source}',
                    style: const TextStyle(fontSize: 10.5, color: AppTheme.textMuted),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPidItem(FlaggedPidModel pid) {
    final langCode = LocaleService.currentLanguageCode;
    final title = pid.simpleTitle.isNotEmpty ? pid.simpleTitle : '${pid.pidName} Outside Expected Range';
    final readingStr = '${pid.observedValue} ${pid.unit}'.trim();
    final whatFound = pid.whatWeFound.isNotEmpty ? pid.whatWeFound : pid.reason;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Sensor Tag + Reading Badge + Status Badge
          Wrap(
            spacing: 8,
            runSpacing: 6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.primaryDark,
                  borderRadius: BorderRadius.circular(5),
                ),
                child: Text(
                  pid.pidName,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 11),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(5),
                  border: Border.all(color: const Color(0xFFFDE68A)),
                ),
                child: Text(
                  '${DiagnosticLocalization.getReadingLabel(langCode)}$readingStr',
                  style: const TextStyle(color: Color(0xFF92400E), fontWeight: FontWeight.w700, fontSize: 11),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                decoration: BoxDecoration(
                  color: AppTheme.cautionAmber.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: AppTheme.cautionAmber.withValues(alpha: 0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.tune_rounded, size: 12, color: AppTheme.cautionAmber),
                    const SizedBox(width: 4),
                    Text(
                      DiagnosticLocalization.getOutsideMonitoringRangeLabel(langCode),
                      style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w700, color: AppTheme.cautionAmber),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Title
          Text(
            title,
            style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
          ),
          const SizedBox(height: 6),

          // What we found
          Text(
            DiagnosticLocalization.getWhatWeFoundLabel(langCode).replaceAll(':', ''),
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 2),
          Text(
            whatFound,
            style: const TextStyle(fontSize: 12.5, color: AppTheme.textMain, height: 1.35),
          ),
          const SizedBox(height: 8),

          // What does this number mean?
          if (pid.valueMeaning.isNotEmpty) ...[
            Text(
              DiagnosticLocalization.getWhatDoesThisNumberMeanLabel(langCode),
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 2),
            Text(
              pid.valueMeaning,
              style: const TextStyle(fontSize: 12.5, color: AppTheme.textMain, height: 1.35),
            ),
            const SizedBox(height: 8),
          ],

          // How often did this happen? (Sample percentage)
          if (pid.sampleExplanation.isNotEmpty || pid.samplePercentageOutside != null) ...[
            Text(
              DiagnosticLocalization.getHowOftenDidThisHappenLabel(langCode),
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 2),
            Text(
              pid.sampleExplanation.isNotEmpty
                  ? pid.sampleExplanation
                  : '${pid.samplePercentageOutside}% of recorded samples were outside the application\'s configured range.',
              style: const TextStyle(fontSize: 12, color: AppTheme.textMain, height: 1.35),
            ),
            const SizedBox(height: 8),
          ],

          // Cross-Finding Notice (e.g. DTC P0171 co-occurrence)
          if (pid.crossFindingNotice != null && pid.crossFindingNotice!.isNotEmpty) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(9),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBEB),
                borderRadius: BorderRadius.circular(7),
                border: Border.all(color: const Color(0xFFFDE68A)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.info_outline, size: 16, color: Color(0xFFB45309)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      pid.crossFindingNotice!,
                      style: const TextStyle(fontSize: 11.5, color: Color(0xFF92400E), height: 1.35, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
          ],

          // What should you do
          if (pid.whatYouShouldDo.isNotEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(9),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(7),
                border: Border.all(color: const Color(0xFFBBF7D0)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.build_circle_outlined, size: 15, color: Color(0xFF15803D)),
                  const SizedBox(width: 7),
                  Expanded(
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(fontSize: 11.5, color: Color(0xFF166534), height: 1.35),
                        children: [
                          TextSpan(
                            text: DiagnosticLocalization.getWhatYouShouldDoLabel(langCode),
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          TextSpan(text: pid.whatYouShouldDo),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Expandable Technical Details, Possible Causes & Limitations
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              tilePadding: EdgeInsets.zero,
              childrenPadding: const EdgeInsets.only(top: 6, bottom: 4),
              title: Text(
                DiagnosticLocalization.getPidPossibleCausesTitle(langCode),
                style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: AppTheme.primaryCobalt),
              ),
              children: [
                if (pid.possibleCauses.isNotEmpty) ...[
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Possible reasons to investigate (Possibilities, not confirmed diagnosis):',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
                    ),
                  ),
                  const SizedBox(height: 3),
                  ...pid.possibleCauses.map((c) => Padding(
                        padding: const EdgeInsets.only(left: 6, bottom: 2),
                        child: Text('• $c', style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3)),
                      )),
                  const SizedBox(height: 6),
                ],
                if (pid.limitations.isNotEmpty) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF3C7),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: const Color(0xFFFDE68A)),
                    ),
                    child: Text(
                      'Important: ${pid.limitations.join(' ')}',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), height: 1.3),
                    ),
                  ),
                  const SizedBox(height: 6),
                ],
                if (pid.rangeSource.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Configured Monitoring Range: ${pid.rangeSource}',
                      style: const TextStyle(fontSize: 10.5, fontStyle: FontStyle.italic, color: AppTheme.textMuted, height: 1.3),
                    ),
                  ),
                  const SizedBox(height: 4),
                ],
                if (pid.technicalDetails.isNotEmpty) ...[
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Technical Context: ${pid.technicalDetails}',
                      style: const TextStyle(fontSize: 11, color: AppTheme.textMuted, height: 1.35),
                    ),
                  ),
                  const SizedBox(height: 4),
                ],
                if (pid.source.isNotEmpty)
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Standard Reference: ${pid.source}',
                      style: const TextStyle(fontSize: 10.5, color: AppTheme.textMuted),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGuidanceCard(InspectionReportModel report) {
    final langCode = LocaleService.currentLanguageCode;
    if (report.guidance.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            DiagnosticLocalization.getNoGuidanceText(langCode),
            style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
        ),
      );
    }

    return Column(
      children: report.guidance.map((passage) => _buildGuidanceItem(passage)).toList(),
    );
  }

  Widget _buildGuidanceItem(KnowledgePassageModel passage) {
    final langCode = LocaleService.currentLanguageCode;
    final drive = passage.canIKeepDriving;
    final localizedDrive = DiagnosticLocalization.getGuidanceCanIKeepDriving(drive, langCode);
    final localizedTitle = DiagnosticLocalization.getGuidanceTitle(passage.title, passage.title, langCode);
    final localizedFound = DiagnosticLocalization.getGuidanceWhatWeFound(passage.whatWeFound, langCode);
    final localizedWhy = DiagnosticLocalization.getGuidanceWhyThisMatters(passage.whyThisMatters, langCode);
    final localizedAction = DiagnosticLocalization.getGuidanceWhatYouShouldDoNow(passage.whatYouShouldDoNow, langCode);
    final localizedChecks = DiagnosticLocalization.getMechanicChecks(passage.whatMechanicMayCheck, langCode);
    final localizedTech = DiagnosticLocalization.getTechnicalDetails(passage.technicalExplanation, langCode);

    Color driveColor = AppTheme.primaryCobalt;
    IconData driveIcon = Icons.info_outline;

    if (drive.toLowerCase().contains('stop in a safe place')) {
      driveColor = AppTheme.unsafeRed;
      driveIcon = Icons.dangerous_rounded;
    } else if (drive.toLowerCase().contains('avoid unnecessary driving')) {
      driveColor = AppTheme.cautionAmber;
      driveIcon = Icons.warning_amber_rounded;
    } else if (drive.toLowerCase().contains('arrange a mechanic')) {
      driveColor = AppTheme.primaryCobalt;
      driveIcon = Icons.calendar_month_outlined;
    } else if (drive.toLowerCase().contains('no immediate action')) {
      driveColor = AppTheme.safeGreen;
      driveIcon = Icons.check_circle_outline;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title & Can I keep driving?
            Text(
              localizedTitle.isNotEmpty ? localizedTitle : 'Safety & Repair Guidance',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
            ),
            if (drive.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                decoration: BoxDecoration(
                  color: driveColor.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: driveColor.withValues(alpha: 0.3)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(driveIcon, size: 16, color: driveColor),
                    const SizedBox(width: 8),
                    Expanded(
                      child: RichText(
                        text: TextSpan(
                          style: TextStyle(fontSize: 12, color: driveColor, height: 1.35),
                          children: [
                            TextSpan(
                              text: DiagnosticLocalization.getCanIKeepDrivingLabel(langCode),
                              style: const TextStyle(fontWeight: FontWeight.w700),
                            ),
                            TextSpan(text: localizedDrive, style: const TextStyle(fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 10),

            // 1. What we found
            RichText(
              text: TextSpan(
                style: const TextStyle(fontSize: 13, height: 1.4, color: AppTheme.textMain),
                children: [
                  TextSpan(
                    text: DiagnosticLocalization.getWhatWeFoundLabel(langCode),
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(text: localizedFound),
                ],
              ),
            ),
            const SizedBox(height: 6),

            // 2. Why this matters
            if (localizedWhy.isNotEmpty) ...[
              RichText(
                text: TextSpan(
                  style: const TextStyle(fontSize: 12.5, height: 1.4, color: AppTheme.textMain),
                  children: [
                    TextSpan(
                      text: DiagnosticLocalization.getWhyThisMattersLabel(langCode),
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    TextSpan(text: localizedWhy),
                  ],
                ),
              ),
              const SizedBox(height: 6),
            ],

            // 3. What you should do now
            if (localizedAction.isNotEmpty) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(9),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(7),
                  border: Border.all(color: const Color(0xFFBBF7D0)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle_outline, size: 15, color: Color(0xFF15803D)),
                    const SizedBox(width: 7),
                    Expanded(
                      child: RichText(
                        text: TextSpan(
                          style: const TextStyle(fontSize: 12, color: Color(0xFF166534), height: 1.35),
                          children: [
                            TextSpan(
                              text: DiagnosticLocalization.getWhatYouShouldDoLabel(langCode),
                              style: const TextStyle(fontWeight: FontWeight.w700),
                            ),
                            TextSpan(text: localizedAction),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 6),
            ],

            // Expandable Technical Details & Mechanic Inspection Areas
            Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                tilePadding: EdgeInsets.zero,
                childrenPadding: const EdgeInsets.only(top: 6, bottom: 4),
                title: Text(
                  DiagnosticLocalization.getMechanicChecklistTitle(langCode),
                  style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: AppTheme.primaryCobalt),
                ),
                children: [
                  if (localizedChecks.isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        DiagnosticLocalization.getWhatMechanicMayCheckLabel(langCode),
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                      ),
                    ),
                    const SizedBox(height: 4),
                    ...localizedChecks.map((c) => Padding(
                          padding: const EdgeInsets.only(left: 6, bottom: 2),
                          child: Text('• $c', style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3)),
                        )),
                    const SizedBox(height: 6),
                  ],
                  if (localizedTech.isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        '${DiagnosticLocalization.getTechnicalDetailsLabel(langCode)}$localizedTech',
                        style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.textMuted, height: 1.35),
                      ),
                    ),
                    const SizedBox(height: 6),
                  ],
                ],
              ),
            ),

            // Citation / Source Reference
            const Divider(color: AppTheme.borderSubtle, height: 14),
            Text(
              '${DiagnosticLocalization.getCitationLabel(langCode)}${passage.documentTitle} (${passage.publisher}), ${passage.section}${passage.url != null ? ' — ${passage.url}' : ''}',
              style: const TextStyle(fontSize: 10.5, fontStyle: FontStyle.italic, color: AppTheme.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // 6. Intelligent Vehicle Repair Cost Estimation Card
  // ---------------------------------------------------------------------------
  Widget _buildRepairCostEstimateCard(InspectionReportModel report) {
    final estimate = _customEstimate ?? report.estimate;
    final langCode = LocaleService.currentLanguageCode;

    if (estimate == null) {
      return Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        elevation: 0,
        color: AppTheme.surfaceLight,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Icon(Icons.calculate_outlined, color: AppTheme.primaryCobalt, size: 22),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      DiagnosticLocalization.getEstimateTitle(langCode),
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              const Text(
                'Calculates genuine Indian market parts prices (Boodmo, PartsBigBoss), bodyshop labour hours, and painting costs.',
                style: TextStyle(fontSize: 12.5, color: AppTheme.textMuted, height: 1.3),
              ),
              const SizedBox(height: 14),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryCobalt,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: _isUpdatingEstimate
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.auto_awesome, size: 18),
                label: Text(
                  _isUpdatingEstimate ? 'Calculating Market Estimate...' : 'Generate Repair & Replacement Estimate',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                ),
                onPressed: _isUpdatingEstimate ? null : () => _refreshEstimate(refreshPricing: true),
              ),
            ],
          ),
        ),
      );
    }

    final isRepairTab = _selectedScenarioTab == 0;
    final activeScenario = isRepairTab ? estimate.repairScenario : estimate.replacementScenario;
    final symbol = activeScenario.currency == 'INR' ? '₹' : '${activeScenario.currency} ';

    // Confidence badge color
    Color confColor = AppTheme.cautionAmber;
    if (estimate.overallConfidence.toLowerCase() == 'strong') {
      confColor = AppTheme.safeGreen;
    } else if (estimate.overallConfidence.toLowerCase() == 'limited') {
      confColor = Colors.orange;
    }

    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: AppTheme.borderSubtle, width: 1.2),
      ),
      elevation: 0,
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Card Title Header
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryCobalt.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.currency_rupee_rounded, color: AppTheme.primaryCobalt, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        DiagnosticLocalization.getEstimateTitle(langCode),
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${estimate.componentDisplayName} • ${DiagnosticLocalization.getExtentName(estimate.extentCategory, langCode)}',
                        style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w500, color: AppTheme.textMuted),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: confColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: confColor.withValues(alpha: 0.3)),
                  ),
                  child: Text(
                    estimate.overallConfidence.toUpperCase(),
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: confColor),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Scenario Tabs (Repair vs Replace)
            Container(
              decoration: BoxDecoration(
                color: AppTheme.surfaceLight,
                borderRadius: BorderRadius.circular(10),
              ),
              padding: const EdgeInsets.all(3),
              child: Row(
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () => setState(() => _selectedScenarioTab = 0),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                        decoration: BoxDecoration(
                          color: isRepairTab ? Colors.white : Colors.transparent,
                          borderRadius: BorderRadius.circular(8),
                          boxShadow: isRepairTab
                              ? [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 4, offset: const Offset(0, 1))]
                              : null,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Flexible(
                              child: Text(
                                DiagnosticLocalization.getScenarioRepairLabel(langCode),
                                textAlign: TextAlign.center,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: isRepairTab ? FontWeight.w700 : FontWeight.w500,
                                  color: isRepairTab ? AppTheme.primaryCobalt : AppTheme.textMuted,
                                ),
                              ),
                            ),
                            if (estimate.repairScenario.isRecommended)
                              const Padding(
                                padding: EdgeInsets.only(left: 4),
                                child: Icon(Icons.star_rounded, size: 14, color: AppTheme.safeGreen),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () => setState(() => _selectedScenarioTab = 1),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                        decoration: BoxDecoration(
                          color: !isRepairTab ? Colors.white : Colors.transparent,
                          borderRadius: BorderRadius.circular(8),
                          boxShadow: !isRepairTab
                              ? [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 4, offset: const Offset(0, 1))]
                              : null,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Flexible(
                              child: Text(
                                DiagnosticLocalization.getScenarioReplaceLabel(langCode),
                                textAlign: TextAlign.center,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: !isRepairTab ? FontWeight.w700 : FontWeight.w500,
                                  color: !isRepairTab ? AppTheme.primaryCobalt : AppTheme.textMuted,
                                ),
                              ),
                            ),
                            if (estimate.replacementScenario.isRecommended)
                              const Padding(
                                padding: EdgeInsets.only(left: 4),
                                child: Icon(Icons.star_rounded, size: 14, color: AppTheme.safeGreen),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Active Scenario Recommendation & Feasibility Banner
            if (activeScenario.isRecommended)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.safeGreen.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.safeGreen.withValues(alpha: 0.25)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_rounded, size: 15, color: AppTheme.safeGreen),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '${DiagnosticLocalization.getRecommendedBadge(langCode)}: ${activeScenario.feasibilityReason}',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.safeGreen),
                      ),
                    ),
                  ],
                ),
              )
            else if (activeScenario.feasibility == 'not_recommended')
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.unsafeRed.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.unsafeRed.withValues(alpha: 0.25)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, size: 15, color: AppTheme.unsafeRed),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        activeScenario.feasibilityReason,
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.unsafeRed),
                      ),
                    ),
                  ],
                ),
              ),

            // Expected Cost Highlight Box
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.surfaceLight,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    DiagnosticLocalization.getExpectedCostLabel(langCode),
                    style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w500, color: AppTheme.textMuted),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.baseline,
                    textBaseline: TextBaseline.alphabetic,
                    children: [
                      Text(
                        '$symbol${activeScenario.expected.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: AppTheme.primaryDark),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '${DiagnosticLocalization.getCostRangeLabel(langCode)}:\n$symbol${activeScenario.minimum.toStringAsFixed(0)} – $symbol${activeScenario.maximum.toStringAsFixed(0)}',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted, height: 1.25),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Itemized Breakdown Expansion Tile
            Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                initiallyExpanded: true,
                tilePadding: EdgeInsets.zero,
                childrenPadding: const EdgeInsets.only(top: 4, bottom: 4),
                title: Text(
                  '${DiagnosticLocalization.getItemizedBreakdownLabel(langCode)} (${activeScenario.breakdown.length} items)',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                ),
                children: [
                  ...activeScenario.breakdown.map((item) {
                    final catLabel = DiagnosticLocalization.getCategoryName(item.category, langCode);
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppTheme.surfaceLight,
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: AppTheme.borderSubtle),
                            ),
                            child: Text(
                              catLabel,
                              style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              item.description,
                              style: const TextStyle(fontSize: 11.5, color: AppTheme.textMain, height: 1.3),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '$symbol${item.totalCost.toStringAsFixed(0)}',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),

            // Online Parts Sources & Provenance Expansion Tile
            if (estimate.sources.isNotEmpty) ...[
              const Divider(color: AppTheme.borderSubtle, height: 16),
              Theme(
                data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                child: ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  childrenPadding: const EdgeInsets.only(top: 4, bottom: 4),
                  title: Text(
                    DiagnosticLocalization.getSourcesProvenanceLabel(langCode),
                    style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700, color: AppTheme.primaryCobalt),
                  ),
                  children: [
                    ...estimate.sources.map((src) {
                      return Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceLight,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  src.sourceName,
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                                ),
                                Text(
                                  '$symbol${src.advertisedPrice.toStringAsFixed(0)}',
                                  style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w800, color: AppTheme.safeGreen),
                                ),
                              ],
                            ),
                            const SizedBox(height: 2),
                            Text(
                              src.productTitle,
                              style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                            if (src.partNumber != null) ...[
                              const SizedBox(height: 2),
                              Text(
                                'Part #${src.partNumber} • Verified: ${src.retrievedAt.substring(0, 10)}',
                                style: const TextStyle(fontSize: 10, color: AppTheme.textMuted, fontStyle: FontStyle.italic),
                              ),
                            ],
                            const SizedBox(height: 4),
                            Text(
                              src.sourceUrl,
                              style: const TextStyle(fontSize: 10, color: AppTheme.primaryCobalt, decoration: TextDecoration.underline),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 12),

            // Action Buttons: Confirm/Edit Component & Refresh Live Pricing
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      side: const BorderSide(color: AppTheme.primaryCobalt),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    icon: const Icon(Icons.edit_note_rounded, size: 16, color: AppTheme.primaryCobalt),
                    label: Text(
                      DiagnosticLocalization.getConfirmComponentButton(langCode),
                      style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: AppTheme.primaryCobalt),
                    ),
                    onPressed: () => _showComponentOverrideSheet(estimate),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  tooltip: DiagnosticLocalization.getRefreshPricingButton(langCode),
                  style: IconButton.styleFrom(
                    backgroundColor: AppTheme.surfaceLight,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: _isUpdatingEstimate
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.refresh_rounded, size: 18, color: AppTheme.primaryDark),
                  onPressed: _isUpdatingEstimate ? null : () => _refreshEstimate(refreshPricing: true),
                ),
              ],
            ),

            const SizedBox(height: 8),
            // Indicative Disclaimer
            Text(
              DiagnosticLocalization.getIndicativeDisclaimer(langCode),
              style: const TextStyle(fontSize: 9.5, fontStyle: FontStyle.italic, color: AppTheme.textMuted, height: 1.3),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Component Confirmation & Override Modal Sheet
  // ---------------------------------------------------------------------------
  void _showComponentOverrideSheet(RepairEstimateModel currentEstimate) {
    String selectedComp = currentEstimate.componentId;
    String selectedExtent = currentEstimate.extentCategory;
    final langCode = LocaleService.currentLanguageCode;

    final componentOptions = [
      {'id': 'front_bumper', 'name': 'Front Bumper Cover'},
      {'id': 'rear_bumper', 'name': 'Rear Bumper Cover'},
      {'id': 'front_grille', 'name': 'Front Grille / Fascia'},
      {'id': 'headlight', 'name': 'Headlight Assembly'},
      {'id': 'taillight', 'name': 'Taillight Assembly'},
      {'id': 'side_mirror', 'name': 'Outside Rear View Mirror (ORVM)'},
      {'id': 'windshield', 'name': 'Front Windshield Glass'},
      {'id': 'front_fender', 'name': 'Front Fender Wing'},
      {'id': 'hood', 'name': 'Engine Hood / Bonnet'},
      {'id': 'door', 'name': 'Side Door Panel'},
      {'id': 'rear_quarter_panel', 'name': 'Rear Quarter Panel'},
      {'id': 'trunk_lid', 'name': 'Trunk Lid / Tailgate'},
    ];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return SafeArea(
              child: Padding(
                padding: EdgeInsets.only(
                  left: 20,
                  right: 20,
                  top: 20,
                  bottom: MediaQuery.of(context).viewInsets.bottom + 20,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      DiagnosticLocalization.getConfirmComponentButton(langCode),
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppTheme.primaryDark),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Select the verified physical component and damage extent to update repair & replacement pricing.',
                      style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    ),
                    const SizedBox(height: 16),

                    // Component Dropdown
                    const Text('Vehicle Component', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      initialValue: selectedComp,
                      decoration: InputDecoration(
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      items: componentOptions.map((opt) {
                        return DropdownMenuItem<String>(
                          value: opt['id'],
                          child: Text(opt['name']!, style: const TextStyle(fontSize: 13)),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) setModalState(() => selectedComp = val);
                      },
                    ),
                    const SizedBox(height: 16),

                    // Damage Extent Selector
                    const Text('Damage Extent Category', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                    const SizedBox(height: 8),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'minor', label: Text('Minor')),
                        ButtonSegment(value: 'moderate', label: Text('Moderate')),
                        ButtonSegment(value: 'extensive', label: Text('Extensive')),
                      ],
                      selected: {selectedExtent},
                      onSelectionChanged: (newSelection) {
                        setModalState(() => selectedExtent = newSelection.first);
                      },
                    ),
                    const SizedBox(height: 20),

                    // Submit Button
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        backgroundColor: AppTheme.primaryCobalt,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      onPressed: () {
                        Navigator.pop(ctx);
                        _applyComponentOverride(selectedComp, selectedExtent);
                      },
                      child: const Text('Update Cost Estimate', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _applyComponentOverride(String componentId, String extentCategory) async {
    setState(() => _isUpdatingEstimate = true);
    try {
      final updated = await ApiClient.updateEstimate(
        widget.inspectionId,
        componentId: componentId,
        extentCategory: extentCategory,
        refreshPricing: false,
      );
      if (!mounted) return;
      setState(() {
        _customEstimate = updated;
        _selectedScenarioTab = updated.repairScenario.isRecommended ? 0 : 1;
        _isUpdatingEstimate = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Repair cost estimate updated successfully.')),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isUpdatingEstimate = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to update estimate: $e')),
      );
    }
  }

  Future<void> _refreshEstimate({bool refreshPricing = false}) async {
    setState(() => _isUpdatingEstimate = true);
    try {
      final updated = await ApiClient.updateEstimate(
        widget.inspectionId,
        refreshPricing: refreshPricing,
      );
      if (!mounted) return;
      setState(() {
        _customEstimate = updated;
        _selectedScenarioTab = updated.repairScenario.isRecommended ? 0 : 1;
        _isUpdatingEstimate = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Live automotive market prices refreshed.')),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isUpdatingEstimate = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to refresh pricing: $e')),
      );
    }
  }
}
