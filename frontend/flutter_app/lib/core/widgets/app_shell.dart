import 'package:flutter/material.dart';

import '../../config/routes.dart';
import '../../config/theme.dart';
import '../../features/dashboard/dashboard_page.dart';
import '../../features/onboarding/onboarding_controller.dart';
import '../../features/onboarding/onboarding_page.dart';
import '../../features/reports/reports_page.dart';
import '../../features/settings/settings_page.dart';
import '../../features/upload/upload_page.dart';
import 'error_state.dart';
import 'loading_state.dart';

class AppShell extends StatelessWidget {
  const AppShell({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final pages = [
          OnboardingPage(controller: controller),
          DashboardPage(controller: controller),
          UploadPage(controller: controller),
          ReportsPage(controller: controller),
          SettingsPage(controller: controller),
        ];

        return LayoutBuilder(
          builder: (context, constraints) {
            final wide = constraints.maxWidth >= 900;
            return Scaffold(
              appBar: AppBar(
                title: Row(
                  children: [
                    Container(
                      width: 34,
                      height: 34,
                      decoration: BoxDecoration(
                        color: AppTheme.leaf,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.balance, color: Colors.white, size: 20),
                    ),
                    const SizedBox(width: 12),
                    const Text('NyayaLens'),
                  ],
                ),
                actions: [
                  if (controller.busy)
                    const Padding(
                      padding: EdgeInsets.only(right: 16),
                      child: LoadingState(),
                    )
                  else
                    Padding(
                      padding: const EdgeInsets.only(right: 16),
                      child: _HealthPill(online: controller.backendOnline),
                    ),
                ],
              ),
              body: Row(
                children: [
                  if (wide)
                    NavigationRail(
                      selectedIndex: controller.selectedIndex,
                      onDestinationSelected: controller.selectTab,
                      labelType: NavigationRailLabelType.all,
                      destinations: const [
                        NavigationRailDestination(
                          icon: Icon(Icons.space_dashboard_outlined),
                          selectedIcon: Icon(Icons.space_dashboard),
                          label: Text('Workspace'),
                        ),
                        NavigationRailDestination(
                          icon: Icon(Icons.monitor_heart_outlined),
                          selectedIcon: Icon(Icons.monitor_heart),
                          label: Text('Dashboard'),
                        ),
                        NavigationRailDestination(
                          icon: Icon(Icons.upload_file_outlined),
                          selectedIcon: Icon(Icons.upload_file),
                          label: Text('Upload'),
                        ),
                        NavigationRailDestination(
                          icon: Icon(Icons.article_outlined),
                          selectedIcon: Icon(Icons.article),
                          label: Text('Reports'),
                        ),
                        NavigationRailDestination(
                          icon: Icon(Icons.settings_outlined),
                          selectedIcon: Icon(Icons.settings),
                          label: Text('Settings'),
                        ),
                      ],
                    ),
                  Expanded(
                    child: Column(
                      children: [
                        if (controller.error != null)
                          Padding(
                            padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
                            child: ErrorState(
                              message: controller.error!,
                              onDismiss: controller.clearNotice,
                            ),
                          ),
                        if (controller.message != null)
                          Padding(
                            padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
                            child: _MessageBar(
                              message: controller.message!,
                              onDismiss: controller.clearNotice,
                            ),
                          ),
                        Expanded(
                          child: IndexedStack(
                            index: controller.selectedIndex,
                            children: pages,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              bottomNavigationBar: wide
                  ? null
                  : NavigationBar(
                      selectedIndex: controller.selectedIndex,
                      onDestinationSelected: controller.selectTab,
                      destinations: AppRoute.values
                          .map(
                            (route) => NavigationDestination(
                              icon: Icon(_iconFor(route, selected: false)),
                              selectedIcon: Icon(_iconFor(route, selected: true)),
                              label: route.label,
                            ),
                          )
                          .toList(),
                    ),
            );
          },
        );
      },
    );
  }

  static IconData _iconFor(AppRoute route, {required bool selected}) {
    return switch (route) {
      AppRoute.onboarding =>
        selected ? Icons.space_dashboard : Icons.space_dashboard_outlined,
      AppRoute.dashboard => selected ? Icons.monitor_heart : Icons.monitor_heart_outlined,
      AppRoute.upload => selected ? Icons.upload_file : Icons.upload_file_outlined,
      AppRoute.reports => selected ? Icons.article : Icons.article_outlined,
      AppRoute.settings => selected ? Icons.settings : Icons.settings_outlined,
    };
  }
}

class _HealthPill extends StatelessWidget {
  const _HealthPill({required this.online});

  final bool online;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(
        online ? Icons.check_circle : Icons.radio_button_unchecked,
        color: online ? AppTheme.leaf : Theme.of(context).colorScheme.outline,
        size: 18,
      ),
      label: Text(online ? 'Online' : 'Not checked'),
    );
  }
}

class _MessageBar extends StatelessWidget {
  const _MessageBar({
    required this.message,
    required this.onDismiss,
  });

  final String message;
  final VoidCallback onDismiss;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFE9F4EE),
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.check_circle_outline, color: AppTheme.leaf),
            const SizedBox(width: 10),
            Expanded(child: Text(message)),
            IconButton(
              tooltip: 'Dismiss',
              onPressed: onDismiss,
              icon: const Icon(Icons.close),
            ),
          ],
        ),
      ),
    );
  }
}
