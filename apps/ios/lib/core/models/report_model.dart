class DetectionModel {
  final String instanceId;
  final String label;
  final double confidence;
  final List<double> bboxXyxy;
  final String coordinateSpace;
  final List<List<double>>? mask;
  final double? maskPixelArea;
  final double? relativeArea;
  /// Prioritization (backend-stamped): 'primary' | 'secondary'.
  final String priority;
  /// Positional component estimate (hood, grille_fascia, front_bumper,
  /// headlight, ...). Advisory heuristic, not trained part output.
  final String? component;
  final double? priorityScore;

  DetectionModel({
    required this.instanceId,
    required this.label,
    required this.confidence,
    required this.bboxXyxy,
    this.coordinateSpace = 'original_image_pixels',
    this.mask,
    this.maskPixelArea,
    this.relativeArea,
    this.priority = 'secondary',
    this.component,
    this.priorityScore,
  });

  factory DetectionModel.fromJson(Map<String, dynamic> json) {
    final rawBox = (json['bbox_xyxy'] as List<dynamic>?)
            ?.map((e) => (e as num).toDouble())
            .toList() ??
        [0.0, 0.0, 0.0, 0.0];

    List<List<double>>? polygon;
    if (json['mask'] != null) {
      polygon = (json['mask'] as List<dynamic>)
          .map((pt) => (pt as List<dynamic>).map((c) => (c as num).toDouble()).toList())
          .toList();
    }

    return DetectionModel(
      instanceId: json['instance_id'] as String? ?? '',
      label: json['label'] as String? ?? 'damage',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      bboxXyxy: rawBox,
      coordinateSpace: json['coordinate_space'] as String? ?? 'original_image_pixels',
      mask: polygon,
      maskPixelArea: (json['mask_pixel_area'] as num?)?.toDouble(),
      relativeArea: (json['relative_area'] as num?)?.toDouble(),
      priority: json['priority'] as String? ?? 'secondary',
      component: json['component'] as String?,
      priorityScore: (json['priority_score'] as num?)?.toDouble(),
    );
  }
}

class ImageFindingModel {
  final String imageId;
  final String? fileId;
  final String? imageUrl;
  final String filename;
  final bool damageDetected;
  /// Tri-state: 'damaged' | 'no_damage' | 'inconclusive'.
  /// Defaults to 'inconclusive' when absent so old payloads never render as NO DAMAGE.
  final String assessment;
  final String? assessmentReason;
  final double? damageProbability;
  final int? originalWidth;
  final int? originalHeight;
  final List<DetectionModel> detections;
  final Map<String, dynamic> severity;

  ImageFindingModel({
    required this.imageId,
    this.fileId,
    this.imageUrl,
    required this.filename,
    required this.damageDetected,
    this.assessment = 'inconclusive',
    this.assessmentReason,
    this.damageProbability,
    this.originalWidth,
    this.originalHeight,
    this.detections = const [],
    this.severity = const {},
  });

  factory ImageFindingModel.fromJson(Map<String, dynamic> json) {
    final dets = (json['detections'] as List<dynamic>?)
            ?.map((e) => DetectionModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    final damageDetected = json['damage_detected'] as bool? ?? false;
    final rawAssessment = json['assessment'] as String?;

    return ImageFindingModel(
      imageId: json['image_id'] as String? ?? '',
      fileId: json['file_id'] as String?,
      imageUrl: json['image_url'] as String?,
      filename: json['filename'] as String? ?? 'image.jpg',
      damageDetected: damageDetected,
      assessment: rawAssessment ??
          (damageDetected ? 'damaged' : 'inconclusive'),
      assessmentReason: json['assessment_reason'] as String?,
      damageProbability: (json['damage_probability'] as num?)?.toDouble(),
      originalWidth: (json['original_width'] as num?)?.toInt(),
      originalHeight: (json['original_height'] as num?)?.toInt(),
      detections: dets,
      severity: json['severity'] as Map<String, dynamic>? ?? {},
    );
  }
}

class FlaggedPidModel {
  final String pidName;
  final double observedValue;
  final String unit;
  final String reason;

  FlaggedPidModel({
    required this.pidName,
    required this.observedValue,
    required this.unit,
    required this.reason,
  });

  factory FlaggedPidModel.fromJson(Map<String, dynamic> json) {
    return FlaggedPidModel(
      pidName: json['pid_name'] as String? ?? '',
      observedValue: (json['observed_value'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
    );
  }
}

class DtcModel {
  final String code;
  final String description;
  final String severity;
  final bool escalateRisk;

  DtcModel({
    required this.code,
    required this.description,
    required this.severity,
    required this.escalateRisk,
  });

  factory DtcModel.fromJson(Map<String, dynamic> json) {
    return DtcModel(
      code: json['code'] as String? ?? '',
      description: json['description'] as String? ?? '',
      severity: json['severity'] as String? ?? 'moderate',
      escalateRisk: json['escalate_risk'] as bool? ?? false,
    );
  }
}

class KnowledgePassageModel {
  final String passageId;
  final String content;
  final String documentTitle;
  final String publisher;
  final String section;

  KnowledgePassageModel({
    required this.passageId,
    required this.content,
    required this.documentTitle,
    required this.publisher,
    required this.section,
  });

  factory KnowledgePassageModel.fromJson(Map<String, dynamic> json) {
    final cite = json['citation'] as Map<String, dynamic>? ?? {};
    return KnowledgePassageModel(
      passageId: json['passage_id'] as String? ?? '',
      content: json['content'] as String? ?? '',
      documentTitle: cite['document_title'] as String? ?? 'Safety Bulletin',
      publisher: cite['publisher'] as String? ?? 'Automotive Authority',
      section: cite['section'] as String? ?? '',
    );
  }
}

class InspectionReportModel {
  final String inspectionId;
  final String generatedAt;
  final bool damageDetected;
  /// Tri-state overall verdict: 'damaged' | 'no_damage' | 'inconclusive'.
  /// Defaults to 'inconclusive' when absent so old payloads never render as NO DAMAGE.
  final String assessment;
  final String? assessmentReason;
  final String overallSummary;
  final String riskClass;
  final String riskSummary;
  final List<String> riskReasons;
  final bool reviewRequired;
  final double? severityScore;
  final String severityLevel;
  final List<ImageFindingModel> images;
  final String obdStatus;
  final bool? obdAnomalyDetected;
  final List<FlaggedPidModel> flaggedPids;
  final List<DtcModel> dtcs;
  final List<KnowledgePassageModel> guidance;
  final String disclaimer;

  InspectionReportModel({
    required this.inspectionId,
    required this.generatedAt,
    required this.damageDetected,
    this.assessment = 'inconclusive',
    this.assessmentReason,
    required this.overallSummary,
    required this.riskClass,
    required this.riskSummary,
    required this.riskReasons,
    required this.reviewRequired,
    this.severityScore,
    required this.severityLevel,
    required this.images,
    required this.obdStatus,
    this.obdAnomalyDetected,
    required this.flaggedPids,
    required this.dtcs,
    required this.guidance,
    required this.disclaimer,
  });

  factory InspectionReportModel.fromJson(Map<String, dynamic> json) {
    final overall = json['overall'] as Map<String, dynamic>? ?? {};
    final risk = json['risk'] as Map<String, dynamic>? ?? {};
    final sev = json['severity'] as Map<String, dynamic>? ?? {};
    final obd = json['obd'] as Map<String, dynamic>? ?? {};
    final know = json['knowledge'] as Map<String, dynamic>? ?? {};

    final imgList = (json['images'] as List<dynamic>?)
            ?.map((e) => ImageFindingModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    final pids = (obd['flagged_pids'] as List<dynamic>?)
            ?.map((e) => FlaggedPidModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    final dtcList = (obd['dtcs'] as List<dynamic>?)
            ?.map((e) => DtcModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    final passages = (know['passages'] as List<dynamic>?)
            ?.map((e) => KnowledgePassageModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    final reasons = (risk['reason_codes'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        [];

    final damageDetected = overall['damage_detected'] as bool? ?? false;
    final rawAssessment = overall['assessment'] as String?;

    return InspectionReportModel(
      inspectionId: json['inspection_id'] as String? ?? '',
      generatedAt: json['generated_at'] as String? ?? '',
      damageDetected: damageDetected,
      assessment: rawAssessment ?? (damageDetected ? 'damaged' : 'inconclusive'),
      assessmentReason: overall['assessment_reason'] as String?,
      overallSummary: overall['summary'] as String? ?? 'Inspection complete.',
      riskClass: (risk['class'] as String? ?? 'unavailable').toLowerCase(),
      riskSummary: risk['summary'] as String? ?? '',
      riskReasons: reasons,
      reviewRequired: risk['review_required'] as bool? ?? false,
      severityScore: (sev['score'] as num?)?.toDouble(),
      severityLevel: (sev['level'] as String? ?? 'low').toLowerCase(),
      images: imgList,
      obdStatus: obd['status'] as String? ?? 'not_provided',
      obdAnomalyDetected: obd['anomaly_detected'] as bool?,
      flaggedPids: pids,
      dtcs: dtcList,
      guidance: passages,
      disclaimer: json['disclaimer'] as String? ??
          'AI-assisted decision support only. Not a roadworthiness guarantee.',
    );
  }
}
