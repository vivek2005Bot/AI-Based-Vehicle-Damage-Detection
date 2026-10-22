import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/api_config.dart';
import '../localization/locale_service.dart';
import '../models/inspection_model.dart';
import '../models/report_model.dart';
import '../models/user_model.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiClient {
  static Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Accept-Language': LocaleService.currentLanguageCode,
    };
    if (ApiConfig.currentToken != null) {
      headers['Authorization'] = 'Bearer ${ApiConfig.currentToken}';
    }
    return headers;
  }

  // --- Auth ---

  static Future<String> login(String email, String password) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/auth/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final token = data['access_token'] as String;
      await ApiConfig.setToken(token);
      return token;
    } else {
      final err = _extractErrorMessage(response);
      throw ApiException(err, response.statusCode);
    }
  }

  static Future<UserModel> register(String email, String password) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/auth/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 201) {
      return UserModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      final err = _extractErrorMessage(response);
      throw ApiException(err, response.statusCode);
    }
  }

  static Future<UserModel> getMe() async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/auth/me');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw ApiException('Failed to retrieve user profile', response.statusCode);
    }
  }

  // --- Inspections ---

  static Future<List<InspectionModel>> listInspections() async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => InspectionModel.fromJson(e as Map<String, dynamic>)).toList();
    } else {
      throw ApiException('Failed to list inspections', response.statusCode);
    }
  }

  static Future<InspectionModel> createInspection({
    String? make,
    String? model,
    int? year,
    double? mileage,
    String mileageUnit = 'km',
    String? vin,
  }) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({
        'make': make,
        'model': model,
        'year': year,
        'mileage': mileage,
        'mileage_unit': mileageUnit,
        'vin': vin,
      }),
    );

    if (response.statusCode == 201) {
      return InspectionModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static Future<InspectionModel> getInspection(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      return InspectionModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw ApiException('Inspection not found', response.statusCode);
    }
  }

  // --- File Uploads ---

  static Future<void> uploadImages(String inspectionId, List<File> imageFiles) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/images');
    final request = http.MultipartRequest('POST', url);

    if (ApiConfig.currentToken != null) {
      request.headers['Authorization'] = 'Bearer ${ApiConfig.currentToken}';
    }

    for (final file in imageFiles) {
      final bytes = await file.readAsBytes();
      final filename = file.path.split('/').last;
      final ext = filename.split('.').last.toLowerCase();
      final mime = ext == 'png' ? 'image/png' : 'image/jpeg';

      request.files.add(http.MultipartFile.fromBytes(
        'images',
        bytes,
        filename: filename,
        contentType: MediaType.parse(mime),
      ));
    }

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static Future<void> uploadObdCsv(String inspectionId, File csvFile) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/obd');
    final request = http.MultipartRequest('POST', url);

    if (ApiConfig.currentToken != null) {
      request.headers['Authorization'] = 'Bearer ${ApiConfig.currentToken}';
    }

    final bytes = await csvFile.readAsBytes();
    final filename = csvFile.path.split('/').last;

    request.files.add(http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: filename,
      contentType: MediaType('text', 'csv'),
    ));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  // --- Analysis & Status ---

  static Future<String> triggerAnalysis(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/analyze');
    final response = await http.post(url, headers: _headers);

    if (response.statusCode == 202) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['job_id'] as String;
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static Future<Map<String, dynamic>> getStatus(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/status');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw ApiException('Failed to retrieve inspection status', response.statusCode);
    }
  }

  // --- Reports ---

  static Future<InspectionReportModel> getReport(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/report');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return InspectionReportModel.fromJson(data);
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static String get currentBaseUrlForUrl => ApiConfig.currentBaseUrl;

  static String imageContentUrl(String inspectionId, String fileId) {
    return '${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/images/$fileId/content';
  }

  static Future<Uint8List> getInspectionImageBytes(String inspectionId, String fileId) async {
    final url = Uri.parse(imageContentUrl(inspectionId, fileId));
    final response = await http.get(url, headers: _headers);
    if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
      return response.bodyBytes;
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static Future<void> deleteInspection(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId');
    final response = await http.delete(url, headers: _headers);
    if (response.statusCode != 204 && response.statusCode != 200) {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }


  static Future<Uint8List> downloadPdf(String inspectionId, {String? locale}) async {
    final lang = locale ?? LocaleService.currentLanguageCode;
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/report.pdf?locale=$lang');
    final response = await http.get(url, headers: _headers);

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw ApiException('Failed to download PDF report', response.statusCode);
    }
  }

  static Future<RepairEstimateModel> getEstimate(String inspectionId) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/estimate');
    final response = await http.get(url, headers: _headers);
    if (response.statusCode == 200) {
      return RepairEstimateModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }

  static Future<RepairEstimateModel> updateEstimate(
    String inspectionId, {
    String? componentId,
    String? damageType,
    String? extentCategory,
    String? make,
    String? model,
    int? year,
    String? city,
    String? oemPreference,
    bool refreshPricing = false,
  }) async {
    final url = Uri.parse('${ApiConfig.currentBaseUrl}/api/v1/inspections/$inspectionId/estimate');
    final payload = <String, dynamic>{
      'refresh_pricing': refreshPricing,
    };
    if (componentId != null) payload['component_id'] = componentId;
    if (damageType != null) payload['damage_type'] = damageType;
    if (extentCategory != null) payload['extent_category'] = extentCategory;
    if (make != null) payload['make'] = make;
    if (model != null) payload['model'] = model;
    if (year != null) payload['year'] = year;
    if (city != null) payload['city'] = city;
    if (oemPreference != null) payload['oem_preference'] = oemPreference;

    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode(payload),
    );
    if (response.statusCode == 200) {
      return RepairEstimateModel.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw ApiException(_extractErrorMessage(response), response.statusCode);
    }
  }


  static String _extractErrorMessage(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      if (data is Map && data.containsKey('detail')) {
        return data['detail'].toString();
      }
      if (data is Map && data.containsKey('error') && data['error'] is Map) {
        return data['error']['message']?.toString() ?? 'Server Error';
      }
    } catch (_) {}
    return 'HTTP Error ${response.statusCode}';
  }
}

