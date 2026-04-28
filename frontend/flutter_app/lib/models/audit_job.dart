class ProjectRecord {
  const ProjectRecord({
    required this.projectId,
    required this.userId,
    required this.name,
    required this.createdAt,
    this.domain,
    this.description,
    this.status = 'created',
  });

  factory ProjectRecord.fromJson(Map<String, dynamic> json) {
    return ProjectRecord(
      projectId: json['project_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      name: json['name'] as String? ?? 'Untitled project',
      domain: json['domain'] as String?,
      description: json['description'] as String?,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
      status: json['status'] as String? ?? 'created',
    );
  }

  final String projectId;
  final String userId;
  final String name;
  final String? domain;
  final String? description;
  final DateTime? createdAt;
  final String status;
}

class UploadRecord {
  const UploadRecord({
    required this.uploadId,
    required this.projectId,
    required this.userId,
    required this.uploadType,
    required this.filename,
    required this.sizeBytes,
    required this.createdAt,
    this.contentType,
    this.status = 'uploaded',
  });

  factory UploadRecord.fromJson(Map<String, dynamic> json) {
    return UploadRecord(
      uploadId: json['upload_id'] as String? ?? '',
      projectId: json['project_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      uploadType: json['upload_type'] as String? ?? 'dataset',
      filename: json['filename'] as String? ?? 'upload',
      contentType: json['content_type'] as String?,
      sizeBytes: json['size_bytes'] as int? ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
      status: json['status'] as String? ?? 'uploaded',
    );
  }

  final String uploadId;
  final String projectId;
  final String userId;
  final String uploadType;
  final String filename;
  final String? contentType;
  final int sizeBytes;
  final DateTime? createdAt;
  final String status;
}

class AuditJob {
  const AuditJob({
    required this.auditId,
    required this.projectId,
    required this.userId,
    required this.auditType,
    required this.status,
    required this.createdAt,
    required this.inputs,
    required this.results,
  });

  factory AuditJob.fromJson(Map<String, dynamic> json) {
    return AuditJob(
      auditId: json['audit_id'] as String? ?? '',
      projectId: json['project_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      auditType: json['audit_type'] as String? ?? 'audit',
      status: json['status'] as String? ?? 'queued',
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
      inputs: Map<String, dynamic>.from(json['inputs'] as Map? ?? {}),
      results: Map<String, dynamic>.from(json['results'] as Map? ?? {}),
    );
  }

  final String auditId;
  final String projectId;
  final String userId;
  final String auditType;
  final String status;
  final DateTime? createdAt;
  final Map<String, dynamic> inputs;
  final Map<String, dynamic> results;
}

class BenchmarkRun {
  const BenchmarkRun({
    required this.benchmarkId,
    required this.projectId,
    required this.status,
    required this.benchmarks,
    required this.createdAt,
  });

  factory BenchmarkRun.fromJson(Map<String, dynamic> json) {
    return BenchmarkRun(
      benchmarkId: json['benchmark_id'] as String? ?? '',
      projectId: json['project_id'] as String? ?? '',
      status: json['status'] as String? ?? 'queued',
      benchmarks: (json['benchmarks'] as List? ?? []).cast<String>(),
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    );
  }

  final String benchmarkId;
  final String projectId;
  final String status;
  final List<String> benchmarks;
  final DateTime? createdAt;
}
