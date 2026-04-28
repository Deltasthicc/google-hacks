import 'package:flutter/material.dart';

import 'config/theme.dart';
import 'core/widgets/app_shell.dart';
import 'features/onboarding/onboarding_controller.dart';

class NyayaLensApp extends StatefulWidget {
  const NyayaLensApp({super.key});

  @override
  State<NyayaLensApp> createState() => _NyayaLensAppState();
}

class _NyayaLensAppState extends State<NyayaLensApp> {
  late final AppController controller;

  @override
  void initState() {
    super.initState();
    controller = AppController();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NyayaLens',
      theme: AppTheme.light(),
      home: AppShell(controller: controller),
    );
  }
}
