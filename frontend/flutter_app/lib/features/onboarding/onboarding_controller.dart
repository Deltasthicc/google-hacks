import 'package:flutter/foundation.dart';

import '../../config/app_config.dart';
import '../../core/constants.dart';
import '../../core/services/api_service.dart';
import '../../core/services/auth_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/utils.dart';
import '../../models/audit_job.dart';
import '../../models/fairness_report.dart';

class AppController extends ChangeNotifier {
  AppController()
      : auth = AuthService(),
        api = ApiService(),
        storage = StorageService();

  final AuthService auth;
  final ApiService api;
  final StorageService storage;

  int selectedIndex = 0;
  bool busy = false;
  bool backendOnline = false;
  String? error;
  String? message;

  String apiBaseUrl = AppConfig.defaultApiBaseUrl;
  String authToken = AppConfig.defaultToken;

  final List<ProjectRecord> projects = [];
  final List<AuditJob> audits = [];
  final List<ReportRecord> reports = [];
  final List<BenchmarkRun> benchmarks = [];

  ProjectRecord? currentProject;
  UploadRecord? datasetUpload;
  UploadRecord? policyUpload;
  PickedUpload? selectedDataset;
  PickedUpload? selectedPolicy;
  ReportRecord? selectedReport;

  String targetColumn = 'approved';
  String predictionColumn = 'prediction';
  List<String> sensitiveColumns = List.of(defaultSensitiveColumns);

  void selectTab(int index) {
    selectedIndex = index;
    notifyListeners();
  }

  void configure({
    required String baseUrl,
    required String token,
  }) {
    apiBaseUrl = baseUrl.trim().isEmpty ? AppConfig.defaultApiBaseUrl : baseUrl.trim();
    authToken = token.trim();
    auth.setToken(authToken);
    api.configure(baseUrl: apiBaseUrl, token: authToken);
    message = 'Workspace settings saved.';
    notifyListeners();
  }

  Future<void> checkHealth() async {
    await _run(() async {
      backendOnline = await api.health();
      message = backendOnline ? 'Backend is online.' : 'Backend did not respond.';
    });
  }

  Future<void> createProject({
    required String name,
    String? domain,
    String? description,
  }) async {
    await _run(() async {
      final project = await api.createProject(
        name: name,
        domain: domain,
        description: description,
      );
      projects.insert(0, project);
      currentProject = project;
      datasetUpload = null;
      policyUpload = null;
      audits.clear();
      reports.clear();
      selectedReport = null;
      selectedIndex = 1;
      message = 'Project created.';
    });
  }

  void chooseProject(ProjectRecord project) {
    currentProject = project;
    selectedIndex = 1;
    notifyListeners();
  }

  Future<void> pickDataset() async {
    final picked = await storage.pickFile(allowedExtensions: ['csv', 'xlsx', 'json']);
    if (picked != null) {
      selectedDataset = picked;
      message = 'Dataset selected.';
      notifyListeners();
    }
  }

  Future<void> pickPolicy() async {
    final picked = await storage.pickFile(allowedExtensions: ['pdf', 'txt', 'docx']);
    if (picked != null) {
      selectedPolicy = picked;
      message = 'Policy document selected.';
      notifyListeners();
    }
  }

  Future<void> uploadDataset() async {
    final project = currentProject;
    final file = selectedDataset;
    if (project == null || file == null) {
      _setError('Select a project and dataset first.');
      return;
    }
    await _run(() async {
      datasetUpload = await api.uploadDataset(
        projectId: project.projectId,
        filename: file.name,
        bytes: file.bytes,
      );
      message = 'Dataset uploaded.';
    });
  }

  Future<void> uploadPolicy() async {
    final project = currentProject;
    final file = selectedPolicy;
    if (project == null || file == null) {
      _setError('Select a project and policy document first.');
      return;
    }
    await _run(() async {
      policyUpload = await api.uploadPolicy(
        projectId: project.projectId,
        filename: file.name,
        bytes: file.bytes,
      );
      message = 'Policy document uploaded.';
    });
  }

  void setAuditInputs({
    required String target,
    required String prediction,
    required String sensitive,
  }) {
    targetColumn = target.trim().isEmpty ? 'approved' : target.trim();
    predictionColumn = prediction.trim().isEmpty ? 'prediction' : prediction.trim();
    sensitiveColumns = parseCsvWords(sensitive);
    if (sensitiveColumns.isEmpty) {
      sensitiveColumns = List.of(defaultSensitiveColumns);
    }
    notifyListeners();
  }

  Future<void> runDataAudit() async {
    final project = currentProject;
    final upload = datasetUpload;
    if (project == null || upload == null) {
      _setError('Create a project and upload a dataset first.');
      return;
    }
    await _run(() async {
      final audit = await api.runDataAudit(
        projectId: project.projectId,
        uploadId: upload.uploadId,
        targetColumn: targetColumn,
        sensitiveColumns: sensitiveColumns,
      );
      audits.insert(0, audit);
      message = 'Data audit queued.';
    });
  }

  Future<void> runModelAudit() async {
    final project = currentProject;
    final upload = datasetUpload;
    if (project == null || upload == null) {
      _setError('Create a project and upload a dataset first.');
      return;
    }
    await _run(() async {
      final audit = await api.runModelAudit(
        projectId: project.projectId,
        uploadId: upload.uploadId,
        targetColumn: targetColumn,
        predictionColumn: predictionColumn,
        sensitiveColumns: sensitiveColumns,
      );
      audits.insert(0, audit);
      message = 'Model audit queued.';
    });
  }

  Future<void> runCounterfactuals() async {
    final project = currentProject;
    if (project == null) {
      _setError('Create a project first.');
      return;
    }
    await _run(() async {
      final latestAudit = audits.isEmpty ? null : audits.first.auditId;
      final audit = await api.runCounterfactuals(
        projectId: project.projectId,
        uploadId: datasetUpload?.uploadId,
        auditId: latestAudit,
        sensitiveColumns: sensitiveColumns,
      );
      audits.insert(0, audit);
      message = 'Counterfactual check queued.';
    });
  }

  Future<void> runBenchmarks() async {
    final project = currentProject;
    if (project == null) {
      _setError('Create a project first.');
      return;
    }
    await _run(() async {
      final run = await api.runBenchmarkSuite(
        projectId: project.projectId,
        benchmarks: benchmarkOptions,
      );
      benchmarks.insert(0, run);
      message = 'Benchmark suite queued.';
    });
  }

  Future<void> generateReport({String mode = 'executive'}) async {
    final project = currentProject;
    if (project == null || audits.isEmpty) {
      _setError('Run an audit before generating a report.');
      return;
    }
    await _run(() async {
      final report = await api.generateReport(
        projectId: project.projectId,
        auditId: audits.first.auditId,
        mode: mode,
      );
      reports.insert(0, report);
      selectedReport = report;
      selectedIndex = 3;
      message = 'Report generated.';
    });
  }

  Future<void> refreshHistory() async {
    final project = currentProject;
    if (project == null) {
      _setError('Create a project first.');
      return;
    }
    await _run(() async {
      final loaded = await api.projectHistory(project.projectId);
      audits
        ..clear()
        ..addAll(loaded.reversed);
      message = 'History refreshed.';
    });
  }

  void selectReport(ReportRecord report) {
    selectedReport = report;
    selectedIndex = 3;
    notifyListeners();
  }

  void clearNotice() {
    error = null;
    message = null;
    notifyListeners();
  }

  Future<void> _run(Future<void> Function() action) async {
    busy = true;
    error = null;
    message = null;
    notifyListeners();
    try {
      await action();
    } on ApiException catch (exc) {
      error = exc.message;
    } catch (exc) {
      error = exc.toString();
    } finally {
      busy = false;
      notifyListeners();
    }
  }

  void _setError(String value) {
    error = value;
    message = null;
    notifyListeners();
  }
}
