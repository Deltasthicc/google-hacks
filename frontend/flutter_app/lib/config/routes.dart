enum AppRoute {
  onboarding('Workspace'),
  dashboard('Dashboard'),
  upload('Upload'),
  reports('Reports'),
  settings('Settings');

  const AppRoute(this.label);

  final String label;
}
