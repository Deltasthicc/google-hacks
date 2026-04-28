import '../../config/app_config.dart';
import '../../models/user_profile.dart';

class AuthService {
  AuthService({
    String token = AppConfig.defaultToken,
  }) : _token = token;

  String _token;

  String get token => _token;

  bool get hasToken => _token.trim().isNotEmpty;

  UserProfile get currentUser => UserProfile(
        userId: hasToken ? _token.trim() : 'local_demo_user',
        authMode: hasToken ? 'bearer_stub' : 'development',
      );

  void setToken(String value) {
    _token = value.trim();
  }
}
