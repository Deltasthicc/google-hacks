class AppConfig {
  static const appName = 'NyayaLens';
  static const defaultApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8080',
  );
  static const defaultToken = String.fromEnvironment(
    'NYAYALENS_DEMO_TOKEN',
    defaultValue: 'local-demo-token',
  );
}
