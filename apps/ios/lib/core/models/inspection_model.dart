class InspectionFileModel {
  final String id;
  final String role;
  final String originalFilename;
  final int byteSize;
  final String mediaType;

  InspectionFileModel({
    required this.id,
    required this.role,
    required this.originalFilename,
    required this.byteSize,
    required this.mediaType,
  });

  factory InspectionFileModel.fromJson(Map<String, dynamic> json) {
    return InspectionFileModel(
      id: json['id'] as String,
      role: json['role'] as String,
      originalFilename: json['original_filename'] as String,
      byteSize: json['byte_size'] as int? ?? 0,
      mediaType: json['media_type'] as String? ?? 'application/octet-stream',
    );
  }
}

class InspectionModel {
  final String id;
  final String userId;
  final String? make;
  final String? model;
  final int? year;
  final double? mileage;
  final String mileageUnit;
  final String? vinMasked;
  final String status;
  final DateTime createdAt;
  final List<InspectionFileModel> files;
  final bool hasReport;
  final String? riskClass;

  InspectionModel({
    required this.id,
    required this.userId,
    this.make,
    this.model,
    this.year,
    this.mileage,
    this.mileageUnit = 'km',
    this.vinMasked,
    required this.status,
    required this.createdAt,
    this.files = const [],
    this.hasReport = false,
    this.riskClass,
  });

  factory InspectionModel.fromJson(Map<String, dynamic> json) {
    final fileList = (json['files'] as List<dynamic>?)
            ?.map((e) => InspectionFileModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    return InspectionModel(
      id: json['id'] as String,
      userId: json['user_id'] as String? ?? '',
      make: json['make'] as String?,
      model: json['model'] as String?,
      year: json['year'] as int?,
      mileage: (json['mileage'] as num?)?.toDouble(),
      mileageUnit: json['mileage_unit'] as String? ?? 'km',
      vinMasked: json['vin_masked'] as String?,
      status: json['status'] as String? ?? 'draft',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      files: fileList,
      hasReport: json['has_report'] as bool? ?? false,
      riskClass: json['risk_class'] as String?,
    );
  }

  String get vehicleDisplayName {
    final parts = [
      if (year != null) '$year',
      if (make != null && make!.isNotEmpty) make!,
      if (model != null && model!.isNotEmpty) model!,
    ];
    return parts.isEmpty ? 'Unnamed Vehicle' : parts.join(' ');
  }
}
