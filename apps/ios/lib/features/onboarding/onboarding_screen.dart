import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../auth/login_screen.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Map<String, dynamic>> _pages = [
    {
      'icon': Icons.camera_alt_rounded,
      'title': 'Multi-Angle Image Capture',
      'desc': 'Capture or upload high-resolution photos of damaged and intact vehicle panels. Our 4-stage vision pipeline detects scratches, dents, glass cracks, and bumper deformation.',
    },
    {
      'icon': Icons.speed_rounded,
      'title': 'OBD-II Telemetry Fusion',
      'desc': 'Upload vehicle CSV logs. Unsupervised Isolation Forest algorithms flag erratic PIDs, sensor over-temperatures, and active Diagnostic Trouble Codes.',
    },
    {
      'icon': Icons.verified_user_rounded,
      'title': 'Grounded Safety Guidance',
      'desc': 'Receive an objective Safe, Caution, or Unsafe drivability assessment grounded in official safety standards and verifiable repair documentation.',
    },
  ];

  void _onNext() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
            child: const Text(
              'Skip',
              style: TextStyle(color: AppTheme.textMuted),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                itemCount: _pages.length,
                onPageChanged: (idx) => setState(() => _currentPage = idx),
                itemBuilder: (context, index) {
                  final page = _pages[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 96,
                          height: 96,
                          decoration: BoxDecoration(
                            color: AppTheme.primaryCobalt.withValues(
                              alpha: 0.1,
                            ),
                            borderRadius: BorderRadius.circular(28),
                          ),
                          child: Icon(
                            page['icon'] as IconData,
                            size: 48,
                            color: AppTheme.primaryCobalt,
                          ),
                        ),
                        const SizedBox(height: 36),
                        Text(
                          page['title'] as String,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                            color: AppTheme.primaryDark,
                            letterSpacing: -0.4,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          page['desc'] as String,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 15,
                            height: 1.45,
                            color: AppTheme.textMuted,
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                _pages.length,
                (i) => Container(
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: _currentPage == i ? 24 : 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _currentPage == i
                        ? AppTheme.primaryCobalt
                        : AppTheme.borderSubtle,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 24.0,
                vertical: 16.0,
              ),
              child: ElevatedButton(
                onPressed: _onNext,
                child: Text(
                  _currentPage == _pages.length - 1 ? 'Get Started' : 'Next',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
