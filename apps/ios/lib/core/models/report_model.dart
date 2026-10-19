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
  /// Original model label before canonical mapping (e.g. CarDD
  /// "glass shatter" -> label "glass_shatter"). Null for classical output.
  final String? sourceLabel;

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
    this.sourceLabel,
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
      sourceLabel: json['source_label'] as String?,
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
  final String rawColumnName;
  final double observedValue;
  final String unit;
  final String reason;
  final String simpleTitle;
  final String whatWeFound;
  final String valueMeaning;
  final double? samplePercentageOutside;
  final int sampleCountEvaluated;
  final int sampleCountOutside;
  final String sampleExplanation;
  final List<double>? configuredRange;
  final String rangeSource;
  final String whatYouShouldDo;
  final List<String> possibleCauses;
  final List<String> limitations;
  final String? crossFindingNotice;
  final String technicalDetails;
  final String source;
  final String directionality;

  FlaggedPidModel({
    required this.pidName,
    this.rawColumnName = '',
    required this.observedValue,
    required this.unit,
    required this.reason,
    this.simpleTitle = '',
    this.whatWeFound = '',
    this.valueMeaning = '',
    this.samplePercentageOutside,
    this.sampleCountEvaluated = 0,
    this.sampleCountOutside = 0,
    this.sampleExplanation = '',
    this.configuredRange,
    this.rangeSource = '',
    this.whatYouShouldDo = '',
    this.possibleCauses = const [],
    this.limitations = const [],
    this.crossFindingNotice,
    this.technicalDetails = '',
    this.source = '',
    this.directionality = '',
  });

  factory FlaggedPidModel.fromJson(Map<String, dynamic> json) {
    final causesList = (json['possible_causes'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];
    final limitsList = (json['limitations'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];
    final rangeList = (json['configured_range'] as List<dynamic>?)
            ?.map((e) => (e as num).toDouble())
            .toList();

    return FlaggedPidModel(
      pidName: json['pid_name'] as String? ?? '',
      rawColumnName: json['raw_column_name'] as String? ?? '',
      observedValue: (json['observed_value'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
      simpleTitle: json['simple_title'] as String? ?? '',
      whatWeFound: json['what_we_found'] as String? ?? '',
      valueMeaning: json['value_meaning'] as String? ?? '',
      samplePercentageOutside: (json['sample_percentage_outside'] as num?)?.toDouble(),
      sampleCountEvaluated: json['sample_count_evaluated'] as int? ?? 0,
      sampleCountOutside: json['sample_count_outside'] as int? ?? 0,
      sampleExplanation: json['sample_explanation'] as String? ?? '',
      configuredRange: rangeList,
      rangeSource: json['range_source'] as String? ?? '',
      whatYouShouldDo: json['what_you_should_do'] as String? ?? '',
      possibleCauses: causesList,
      limitations: limitsList,
      crossFindingNotice: json['cross_finding_notice'] as String?,
      technicalDetails: json['technical_details'] as String? ?? '',
      source: json['source'] as String? ?? '',
      directionality: json['directionality'] as String? ?? '',
    );
  }
}

class DtcModel {
  final String code;
  final String description;
  final String severity;
  final bool escalateRisk;
  final String simpleTitle;
  final String whatItMeans;
  final List<String> whatYouMightNotice;
  final String whatYouShouldDo;
  final String urgency;
  final String urgencyLabel;
  final String whyItMatters;
  final String technicalDetails;
  final List<String> possibleCauses;
  final List<String> limitations;
  final String source;

  DtcModel({
    required this.code,
    required this.description,
    required this.severity,
    required this.escalateRisk,
    this.simpleTitle = '',
    this.whatItMeans = '',
    this.whatYouMightNotice = const [],
    this.whatYouShouldDo = '',
    this.urgency = 'schedule_check',
    this.urgencyLabel = 'Schedule a Check',
    this.whyItMatters = '',
    this.technicalDetails = '',
    this.possibleCauses = const [],
    this.limitations = const [],
    this.source = 'SAE J2012 standard reference',
  });

  factory DtcModel.fromJson(Map<String, dynamic> json) {
    final noticeList = (json['what_you_might_notice'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];
    final causesList = (json['possible_causes'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];
    final limitsList = (json['limitations'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];

    final code = json['code'] as String? ?? '';
    final desc = json['description'] as String? ?? '';
    final title = json['simple_title'] as String? ?? (desc.isNotEmpty ? desc : 'Diagnostic Code $code');

    return DtcModel(
      code: code,
      description: desc,
      severity: json['severity'] as String? ?? 'moderate',
      escalateRisk: json['escalate_risk'] as bool? ?? false,
      simpleTitle: title,
      whatItMeans: json['what_it_means'] as String? ?? desc,
      whatYouMightNotice: noticeList,
      whatYouShouldDo: json['what_you_should_do'] as String? ?? '',
      urgency: json['urgency'] as String? ?? 'schedule_check',
      urgencyLabel: json['urgency_label'] as String? ?? 'Schedule a Check',
      whyItMatters: json['why_it_matters'] as String? ?? '',
      technicalDetails: json['technical_details'] as String? ?? desc,
      possibleCauses: causesList,
      limitations: limitsList,
      source: json['source'] as String? ?? 'SAE J2012 standard reference',
    );
  }
}

class KnowledgePassageModel {
  final String passageId;
  final String content;
  final String documentTitle;
  final String publisher;
  final String section;
  final String? url;
  final String title;
  final String whatWeFound;
  final String whyThisMatters;
  final String whatYouShouldDoNow;
  final String canIKeepDriving;
  final List<String> whatMechanicMayCheck;
  final String technicalExplanation;

  KnowledgePassageModel({
    required this.passageId,
    required this.content,
    required this.documentTitle,
    required this.publisher,
    required this.section,
    this.url,
    this.title = '',
    this.whatWeFound = '',
    this.whyThisMatters = '',
    this.whatYouShouldDoNow = '',
    this.canIKeepDriving = '',
    this.whatMechanicMayCheck = const [],
    this.technicalExplanation = '',
  });

  factory KnowledgePassageModel.fromJson(Map<String, dynamic> json) {
    final cite = json['citation'] as Map<String, dynamic>? ?? {};
    final guidance = json['guidance'] as Map<String, dynamic>? ?? {};
    final checks = (guidance['what_mechanic_may_check'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const [];

    final rawContent = json['content'] as String? ?? '';

    return KnowledgePassageModel(
      passageId: json['passage_id'] as String? ?? '',
      content: rawContent,
      documentTitle: cite['document_title'] as String? ?? 'Safety Standard Bulletin',
      publisher: cite['publisher'] as String? ?? 'Automotive Authority',
      section: cite['section'] as String? ?? '',
      url: cite['url'] as String?,
      title: guidance['title'] as String? ?? 'Verified Safety Guidance',
      whatWeFound: guidance['what_we_found'] as String? ?? rawContent,
      whyThisMatters: guidance['why_this_matters'] as String? ?? '',
      whatYouShouldDoNow: guidance['what_you_should_do_now'] as String? ?? '',
      canIKeepDriving: guidance['can_i_keep_driving'] as String? ?? '',
      whatMechanicMayCheck: checks,
      technicalExplanation: guidance['technical_explanation'] as String? ?? '',
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
  final RepairEstimateModel? estimate;

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
    this.estimate,
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

    RepairEstimateModel? estModel;
    if (json['estimate'] != null && json['estimate'] is Map<String, dynamic>) {
      try {
        estModel = RepairEstimateModel.fromJson(json['estimate'] as Map<String, dynamic>);
      } catch (_) {}
    }

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
      estimate: estModel,
    );
  }
}

class PriceSourceModel {
  final String sourceId;
  final String sourceName;
  final String productTitle;
  final String sourceUrl;
  final double advertisedPrice;
  final String currency;
  final String retrievedAt;
  final String? partNumber;
  final String partTier;
  final double shippingCharge;
  final bool inStock;
  final String reliabilityRating;
  final String? notes;

  PriceSourceModel({
    required this.sourceId,
    required this.sourceName,
    required this.productTitle,
    required this.sourceUrl,
    required this.advertisedPrice,
    this.currency = 'INR',
    required this.retrievedAt,
    this.partNumber,
    this.partTier = 'oem',
    this.shippingCharge = 0.0,
    this.inStock = true,
    this.reliabilityRating = 'high',
    this.notes,
  });

  factory PriceSourceModel.fromJson(Map<String, dynamic> json) {
    return PriceSourceModel(
      sourceId: json['source_id'] as String? ?? '',
      sourceName: json['source_name'] as String? ?? 'Online Parts',
      productTitle: json['product_title'] as String? ?? '',
      sourceUrl: json['source_url'] as String? ?? '',
      advertisedPrice: (json['advertised_price'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'INR',
      retrievedAt: json['retrieved_at'] as String? ?? '',
      partNumber: json['part_number'] as String?,
      partTier: json['part_tier'] as String? ?? 'oem',
      shippingCharge: (json['shipping_charge'] as num?)?.toDouble() ?? 0.0,
      inStock: json['in_stock'] as bool? ?? true,
      reliabilityRating: json['reliability_rating'] as String? ?? 'high',
      notes: json['notes'] as String?,
    );
  }
}

class CostItemModel {
  final String category;
  final String description;
  final String? operation;
  final double quantity;
  final double unitCost;
  final double totalCost;
  final String currency;
  final double? labourHours;
  final double? hourlyRate;
  final String? sourceName;
  final String? sourceUrl;

  CostItemModel({
    required this.category,
    required this.description,
    this.operation,
    this.quantity = 1.0,
    required this.unitCost,
    required this.totalCost,
    this.currency = 'INR',
    this.labourHours,
    this.hourlyRate,
    this.sourceName,
    this.sourceUrl,
  });

  factory CostItemModel.fromJson(Map<String, dynamic> json) {
    return CostItemModel(
      category: json['category'] as String? ?? 'other',
      description: json['description'] as String? ?? '',
      operation: json['operation'] as String?,
      quantity: (json['quantity'] as num?)?.toDouble() ?? 1.0,
      unitCost: (json['unit_cost'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'INR',
      labourHours: (json['labour_hours'] as num?)?.toDouble(),
      hourlyRate: (json['hourly_rate'] as num?)?.toDouble(),
      sourceName: json['source_name'] as String?,
      sourceUrl: json['source_url'] as String?,
    );
  }
}

class EstimateScenarioModel {
  final String scenarioType;
  final String title;
  final bool isRecommended;
  final String feasibility;
  final String feasibilityReason;
  final double minimum;
  final double expected;
  final double maximum;
  final String currency;
  final List<CostItemModel> breakdown;

  EstimateScenarioModel({
    required this.scenarioType,
    required this.title,
    this.isRecommended = false,
    this.feasibility = 'feasible',
    this.feasibilityReason = '',
    required this.minimum,
    required this.expected,
    required this.maximum,
    this.currency = 'INR',
    required this.breakdown,
  });

  factory EstimateScenarioModel.fromJson(Map<String, dynamic> json) {
    final items = (json['breakdown'] as List<dynamic>?)
            ?.map((e) => CostItemModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    return EstimateScenarioModel(
      scenarioType: json['scenario_type'] as String? ?? 'repair',
      title: json['title'] as String? ?? '',
      isRecommended: json['is_recommended'] as bool? ?? false,
      feasibility: json['feasibility'] as String? ?? 'feasible',
      feasibilityReason: json['feasibility_reason'] as String? ?? '',
      minimum: (json['minimum'] as num?)?.toDouble() ?? 0.0,
      expected: (json['expected'] as num?)?.toDouble() ?? 0.0,
      maximum: (json['maximum'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'INR',
      breakdown: items,
    );
  }
}

class RepairEstimateModel {
  final String estimateId;
  final String inspectionId;
  final String status;
  final String componentId;
  final String componentDisplayName;
  final double? componentConfidence;
  final String damageType;
  final double? damageConfidence;
  final String extentCategory;
  final String overallConfidence;
  final String confidenceExplanation;
  final EstimateScenarioModel repairScenario;
  final EstimateScenarioModel replacementScenario;
  final List<PriceSourceModel> sources;
  final List<String> limitations;
  final List<String> missingInformation;

  RepairEstimateModel({
    required this.estimateId,
    required this.inspectionId,
    this.status = 'completed',
    required this.componentId,
    required this.componentDisplayName,
    this.componentConfidence,
    required this.damageType,
    this.damageConfidence,
    this.extentCategory = 'minor',
    this.overallConfidence = 'moderate',
    this.confidenceExplanation = '',
    required this.repairScenario,
    required this.replacementScenario,
    required this.sources,
    this.limitations = const [],
    this.missingInformation = const [],
  });

  factory RepairEstimateModel.fromJson(Map<String, dynamic> json) {
    final dmg = json['damage'] as Map<String, dynamic>? ?? {};
    final repJson = json['repair_scenario'] as Map<String, dynamic>? ?? {};
    final replJson = json['replacement_scenario'] as Map<String, dynamic>? ?? {};
    final srcList = (json['sources'] as List<dynamic>?)
            ?.map((e) => PriceSourceModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    final lims = (json['limitations'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];
    final miss = (json['missing_information'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];

    return RepairEstimateModel(
      estimateId: json['estimate_id'] as String? ?? '',
      inspectionId: json['inspection_id'] as String? ?? '',
      status: json['status'] as String? ?? 'completed',
      componentId: dmg['component_id'] as String? ?? 'front_bumper',
      componentDisplayName: dmg['component_display_name'] as String? ?? 'Front Bumper Cover',
      componentConfidence: (dmg['component_confidence'] as num?)?.toDouble(),
      damageType: dmg['damage_type'] as String? ?? 'scratch',
      damageConfidence: (dmg['damage_confidence'] as num?)?.toDouble(),
      extentCategory: dmg['extent_category'] as String? ?? 'minor',
      overallConfidence: json['overall_confidence'] as String? ?? 'moderate',
      confidenceExplanation: json['confidence_explanation'] as String? ?? '',
      repairScenario: EstimateScenarioModel.fromJson(repJson),
      replacementScenario: EstimateScenarioModel.fromJson(replJson),
      sources: srcList,
      limitations: lims,
      missingInformation: miss,
    );
  }
}
