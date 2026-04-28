class UserProfile {
  const UserProfile({
    required this.userId,
    required this.authMode,
  });

  final String userId;
  final String authMode;

  bool get isLocal => authMode == 'development' || authMode == 'bearer_stub';
}
