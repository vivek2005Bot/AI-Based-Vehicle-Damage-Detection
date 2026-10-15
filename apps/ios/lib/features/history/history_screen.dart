import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../core/models/inspection_model.dart';
import '../../core/networking/api_client.dart';
import '../../core/theme/app_theme.dart';
import '../progress/analysis_progress_screen.dart';
import '../report/report_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<InspectionModel> _allInspections = [];
  List<InspectionModel> _filteredInspections = [];
  bool _isLoading = true;
  String? _errorMessage;
  final TextEditingController _searchController = TextEditingController();
  String _selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    _fetchInspections();
    _searchController.addListener(_applyFilter);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _fetchInspections() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final list = await ApiClient.listInspections();
      if (!mounted) return;
      setState(() {
        _allInspections = list;
        _isLoading = false;
      });
      _applyFilter();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _applyFilter() {
    final query = _searchController.text.trim().toLowerCase();
    setState(() {
      _filteredInspections = _allInspections.where((item) {
        final matchesQuery = query.isEmpty ||
            item.vehicleDisplayName.toLowerCase().contains(query) ||
            item.id.toLowerCase().contains(query);

        if (!matchesQuery) return false;

        if (_selectedFilter == 'all') return true;
        if (_selectedFilter == 'safe') return item.riskClass?.toLowerCase() == 'safe';
        if (_selectedFilter == 'caution') return item.riskClass?.toLowerCase() == 'caution';
        if (_selectedFilter == 'unsafe') return item.riskClass?.toLowerCase() == 'unsafe';
        return true;
      }).toList();
    });
  }

  void _openInspection(InspectionModel item) {
    if (item.status == 'completed' || item.status == 'completed_with_warnings') {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ReportScreen(inspectionId: item.id)),
      ).then((_) => _fetchInspections());
    } else {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => AnalysisProgressScreen(inspectionId: item.id)),
      ).then((_) => _fetchInspections());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspection History'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search Bar & Filter Chips
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10.0),
              child: Column(
                children: [
                  TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search by vehicle make, model, or ID...',
                      prefixIcon: const Icon(Icons.search, color: AppTheme.textMuted),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear, size: 18),
                              onPressed: () => _searchController.clear(),
                            )
                          : null,
                    ),
                  ),
                  const SizedBox(height: 10),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildFilterChip('all', 'All Inspections'),
                        const SizedBox(width: 8),
                        _buildFilterChip('safe', 'Safe'),
                        const SizedBox(width: 8),
                        _buildFilterChip('caution', 'Caution'),
                        const SizedBox(width: 8),
                        _buildFilterChip('unsafe', 'Unsafe'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: AppTheme.borderSubtle),

            // Content
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24.0),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.error_outline, size: 48, color: AppTheme.unsafeRed),
                                const SizedBox(height: 12),
                                Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: AppTheme.textMuted)),
                                const SizedBox(height: 16),
                                ElevatedButton(onPressed: _fetchInspections, child: const Text('Retry')),
                              ],
                            ),
                          ),
                        )
                      : _filteredInspections.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.search_off_rounded, size: 52, color: AppTheme.textMuted.withValues(alpha: 0.4)),
                                  const SizedBox(height: 12),
                                  const Text('No matching inspections found', style: TextStyle(fontWeight: FontWeight.w600, color: AppTheme.primaryDark)),
                                ],
                              ),
                            )
                          : RefreshIndicator(
                              onRefresh: _fetchInspections,
                              child: ListView.separated(
                                padding: const EdgeInsets.all(16),
                                itemCount: _filteredInspections.length,
                                separatorBuilder: (_, _) => const SizedBox(height: 10),
                                itemBuilder: (context, index) {
                                  final item = _filteredInspections[index];
                                  return _buildItemCard(item);
                                },
                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String key, String label) {
    final isSelected = _selectedFilter == key;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        setState(() => _selectedFilter = key);
        _applyFilter();
      },
      selectedColor: AppTheme.primaryCobalt.withValues(alpha: 0.15),
      labelStyle: TextStyle(
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        color: isSelected ? AppTheme.primaryCobalt : AppTheme.textMuted,
      ),
    );
  }

  Widget _buildItemCard(InspectionModel item) {
    Color badgeColor = Colors.grey;
    String badgeText = item.status.toUpperCase();

    if (item.riskClass != null) {
      final rc = item.riskClass!.toLowerCase();
      if (rc == 'safe') {
        badgeColor = AppTheme.safeGreen;
        badgeText = 'SAFE';
      } else if (rc == 'caution') {
        badgeColor = AppTheme.cautionAmber;
        badgeText = 'CAUTION';
      } else if (rc == 'unsafe') {
        badgeColor = AppTheme.unsafeRed;
        badgeText = 'UNSAFE';
      }
    } else if (item.status == 'queued' || item.status == 'processing') {
      badgeColor = AppTheme.accentCyan;
      badgeText = 'PROCESSING';
    }

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        onTap: () => _openInspection(item),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: badgeColor.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(Icons.directions_car_rounded, color: badgeColor, size: 24),
        ),
        title: Text(
          item.vehicleDisplayName,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
        ),
        subtitle: Text(
          '${DateFormat('MMM d, yyyy • HH:mm').format(item.createdAt.toLocal())}\nID: ${item.id.substring(0, 8)}...',
          style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: badgeColor.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: badgeColor.withValues(alpha: 0.3)),
          ),
          child: Text(
            badgeText,
            style: TextStyle(color: badgeColor, fontWeight: FontWeight.w700, fontSize: 11),
          ),
        ),
      ),
    );
  }
}
