import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'locale_service.dart';

class LanguageSelectorWidget extends StatelessWidget {
  final bool compact;
  final Color? backgroundColor;
  final Color? textColor;

  const LanguageSelectorWidget({
    super.key,
    this.compact = false,
    this.backgroundColor,
    this.textColor,
  });

  void _showLanguagePicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return Material(
          color: Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          clipBehavior: Clip.antiAlias,
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.75,
            ),
            child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                margin: const EdgeInsets.only(top: 10, bottom: 6),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                child: Row(
                  children: [
                    const Icon(Icons.language_rounded, color: AppTheme.primaryDark, size: 22),
                    const SizedBox(width: 10),
                    const Text(
                      'Select Language / भाषा चुनें',
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.primaryDark,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close_rounded, size: 20),
                      onPressed: () => Navigator.pop(ctx),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: LocaleService.supportedLanguages.length,
                  separatorBuilder: (_, i) => const Divider(height: 1, indent: 60),
                  itemBuilder: (context, index) {
                    final lang = LocaleService.supportedLanguages[index];
                    final isSelected = lang.code == LocaleService.currentLanguageCode;

                    return ListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 2),
                      leading: Container(
                        width: 38,
                        height: 38,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: isSelected ? AppTheme.primaryDark : AppTheme.surfaceLight,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: isSelected ? AppTheme.primaryDark : AppTheme.borderSubtle,
                          ),
                        ),
                        child: Text(
                          lang.code.toUpperCase(),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: isSelected ? Colors.white : AppTheme.textMuted,
                          ),
                        ),
                      ),
                      title: Text(
                        lang.nativeName,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected ? AppTheme.primaryDark : AppTheme.textMain,
                        ),
                      ),
                      subtitle: Text(
                        lang.name,
                        style: TextStyle(
                          fontSize: 12,
                          color: isSelected ? AppTheme.primaryCobalt : AppTheme.textMuted,
                        ),
                      ),
                      trailing: isSelected
                          ? const Icon(Icons.check_circle_rounded, color: AppTheme.primaryDark, size: 22)
                          : null,
                      onTap: () {
                        LocaleService.setLocale(lang.locale);
                        Navigator.pop(ctx);
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      );
    },
    );
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<Locale>(
      valueListenable: LocaleService.currentLocaleNotifier,
      builder: (context, locale, child) {
        final currentLang = LocaleService.currentLanguage;

        if (compact) {
          return InkWell(
            onTap: () => _showLanguagePicker(context),
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: backgroundColor ?? Colors.white.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.language_rounded, size: 16, color: textColor ?? AppTheme.primaryDark),
                  const SizedBox(width: 5),
                  Text(
                    currentLang.nativeName,
                    style: TextStyle(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w700,
                      color: textColor ?? AppTheme.primaryDark,
                    ),
                  ),
                  const SizedBox(width: 3),
                  Icon(Icons.arrow_drop_down, size: 18, color: textColor ?? AppTheme.primaryDark),
                ],
              ),
            ),
          );
        }

        return InkWell(
          onTap: () => _showLanguagePicker(context),
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: backgroundColor ?? AppTheme.surfaceLight,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppTheme.borderSubtle),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.language_rounded, size: 18, color: AppTheme.primaryDark),
                const SizedBox(width: 8),
                Text(
                  'Language: ',
                  style: TextStyle(
                    fontSize: 12.5,
                    fontWeight: FontWeight.w500,
                    color: textColor ?? AppTheme.textMuted,
                  ),
                ),
                Text(
                  currentLang.nativeName,
                  style: TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: textColor ?? AppTheme.primaryDark,
                  ),
                ),
                const SizedBox(width: 4),
                Icon(Icons.arrow_drop_down, size: 20, color: textColor ?? AppTheme.primaryDark),
              ],
            ),
          ),
        );
      },
    );
  }
}
