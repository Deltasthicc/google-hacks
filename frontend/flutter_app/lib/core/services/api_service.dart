import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../../config/app_config.dart';
import '../../models/audit_job.dart';
import '../../models/fairness_report.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.code = 'API_ERROR'});

  final String message;
  final String code;

  @override
  String toString() => '$code: $message';
}

class ApiService {
  ApiService({
    String baseUrl = AppConfig.defaultApiBaseUrl,
    String token = AppConfig.defaultToken,
    http.Client? client,
  })  : _baseUrl = _normalizeBaseUrl(baseUrl),
        _token = token,
        _client = client ?? http.Client();

  String _baseUrl;
  String _token;
  final http.Client _client;

  String get baseUrl => _baseUrl;

  void configure({
    required String baseUrl,
    required String token,
  }) {
    _baseUrl = _normalizeBaseUrl(baseUrl);
    _token = token.trim();
  }

  Future<bool> health() async {
    final response = await _client.get(Uri.parse('$_baseUrl/health'));
    return response.statusCode == 200;
  }

  Future<ProjectRecord> createProject({
    required String name,
    String? domain,
    String? description,
  }) async {
    final data = await _postJson('/api/v1/projects', {
      'name': name,
      'domain': domain,
      'description': description,
    });
    return ProjectRecord.fromJson(data);
  }

  Future<UploadRecord> uploadDataset({
    required String projectId,
    required String filename,
    required Uint8List bytes,
  }) async {
    final data = await _postMultipart(
      '/api/v1/upload-dataset',
      projectId: projectId,
      filename: filename,
      bytes: bytes,
    );
    return UploadRecord.fromJson(data);
  }

  Future<UploadRecord> uploadPolicy({
    required String projectId,
    required String filename,
    required Uint8List bytes,
  }) async {
    final data = await _postMultipart(
      '/api/v1/upload-policy-doc',
      projectId: projectId,
      filename: filename,
      bytes: bytes,
    );
    return UploadRecord.fromJson(data);
  }

  Future<AuditJob> runDataAudit({
    required String projectId,
    required String uploadId,
    required String targetColumn,
    required List<String> sensitiveColumns,
  }) async {
    final data = await _postJson('/api/v1/run-data-audit', {
      'project_id': projectId,
      'upload_id': uploadId,
      'target_column': targetColumn,
      'sensitive_columns': sensitiveColumns,
    });
    return AuditJob.fromJson(data);
  }

  Future<AuditJob> runModelAudit({
    required String projectId,
    required String uploadId,
    required String targetColumn,
    required String predictionColumn,
    required List<String> sensitiveColumns,
  }) async {
    final data = await _postJson('/api/v1/run-model-audit', {
      'project_id': projectId,
      'upload_id': uploadId,
      'target_column': targetColumn,
      'prediction_column': predictionColumn,
      'sensitive_columns': sensitiveColumns,
    });
    return AuditJob.fromJson(data);
  }

  Future<AuditJob> runCounterfactuals({
    required String projectId,
    String? uploadId,
    String? auditId,
    required List<String> sensitiveColumns,
  }) async {
    final data = await _postJson('/api/v1/run-counterfactuals', {
      'project_id': projectId,
      'upload_id': uploadId,
      'audit_id': auditId,
      'sensitive_columns': sensitiveColumns,
      'sample_limit': 100,
    });
    return AuditJob.fromJson(data);
  }

  Future<BenchmarkRun> runBenchmarkSuite({
    required String projectId,
    required List<String> benchmarks,
  }) async {
    final data = await _postJson('/api/v1/run-benchmark-suite', {
      'project_id': projectId,
      'suite_name': 'default',
      'benchmarks': benchmarks,
    });
    return BenchmarkRun.fromJson(data);
  }

  Future<ReportRecord> generateReport({
    required String projectId,
    required String auditId,
    required String mode,
  }) async {
    final data = await _postJson('/api/v1/generate-report', {
      'project_id': projectId,
      'audit_id': auditId,
      'mode': mode,
    });
    return ReportRecord.fromJson(data);
  }

  Future<List<AuditJob>> projectHistory(String projectId) async {
    final data = await _getJson('/api/v1/project/$projectId/history');
    final audits = data['audits'] as List? ?? [];
    return audits
        .map((item) => AuditJob.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }

  Future<Map<String, dynamic>> _getJson(String path) async {
    final response = await _client.get(_uri(path), headers: _headers());
    return _unwrap(response);
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final response = await _client.post(
      _uri(path),
      headers: _headers(jsonContent: true),
      body: jsonEncode(body),
    );
    return _unwrap(response);
  }

  Future<Map<String, dynamic>> _postMultipart(
    String path, {
    required String projectId,
    required String filename,
    required Uint8List bytes,
  }) async {
    final request = http.MultipartRequest('POST', _uri(path));
    request.headers.addAll(_headers());
    request.fields['project_id'] = projectId;
    request.files.add(
      http.MultipartFile.fromBytes('file', bytes, filename: filename),
    );
    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);
    return _unwrap(response);
  }

  Map<String, String> _headers({bool jsonContent = false}) {
    final headers = <String, String>{};
    if (jsonContent) {
      headers['Content-Type'] = 'application/json';
    }
    if (_token.trim().isNotEmpty) {
      headers['Authorization'] = 'Bearer ${_token.trim()}';
    }
    return headers;
  }

  Uri _uri(String path) => Uri.parse('$_baseUrl$path');

  Map<String, dynamic> _unwrap(http.Response response) {
    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400 || decoded['success'] == false) {
      final error = decoded['error'] as Map? ?? {};
      throw ApiException(
        error['message'] as String? ?? 'Request failed',
        code: error['code'] as String? ?? 'HTTP_${response.statusCode}',
      );
    }
    return Map<String, dynamic>.from(decoded['data'] as Map? ?? {});
  }

  static String _normalizeBaseUrl(String value) {
    final trimmed = value.trim().isEmpty ? AppConfig.defaultApiBaseUrl : value.trim();
    return trimmed.endsWith('/') ? trimmed.substring(0, trimmed.length - 1) : trimmed;
  }
}
