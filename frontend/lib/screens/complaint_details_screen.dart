import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/complaint_model.dart';
import 'package:intl/intl.dart';

class ComplaintDetailsScreen extends StatefulWidget {
  final String complaintId;
  final String? baseUrl;

  const ComplaintDetailsScreen({Key? key, required this.complaintId, this.baseUrl}) : super(key: key);

  @override
  State<ComplaintDetailsScreen> createState() => _ComplaintDetailsScreenState();
}

class _ComplaintDetailsScreenState extends State<ComplaintDetailsScreen> {
  late final ApiService _apiService;
  ComplaintModel? _complaint;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(baseUrl: widget.baseUrl);
    _loadComplaint();
  }

  Future<void> _loadComplaint() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final complaint = await _apiService.getComplaint(widget.complaintId);
      setState(() {
        _complaint = complaint;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Complaint Details'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Error: $_errorMessage'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadComplaint,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _complaint == null
                  ? const Center(child: Text('Complaint not found'))
                  : Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ListView(
                        children: [
                          _buildDetailRow('ID', _complaint!.id),
                          _buildDetailRow('Description', _complaint!.description),
                          _buildDetailRow('Location', _complaint!.location),
                          _buildDetailRow('Citizen ID', _complaint!.citizenId),
                          _buildDetailRow('Status', _complaint!.status),
                          _buildDetailRow(
                              'Assigned Officer',
                              _complaint!.assignedOfficer),
                          _buildDetailRow(
                              'Created At',
                              DateFormat.yMMMd().add_jm()
                                  .format(_complaint!.createdAt)),
                          _buildDetailRow(
                              'Updated At',
                              DateFormat.yMMMd().add_jm()
                                  .format(_complaint!.updatedAt)),
                          if (_complaint!.resolvedAt != null)
                            _buildDetailRow(
                                'Resolved At',
                                DateFormat.yMMMd().add_jm()
                                    .format(_complaint!.resolvedAt!)),
                          const Divider(height: 32),
                          _buildSLASection(),
                          const Divider(height: 32),
                          _buildAIAnalysisSection(),
                        ],
                      ),
                    ),
          );
  }

  Widget _buildDetailRow(String label, String? value,
      {String? status, bool? escalated}) {
    final String displayValue = value ?? 'N/A';

    // Determine text color based on status or escalation
    Color textColor = Colors.black;

    if (status != null) {
      switch (status) {
        case 'ON_TRACK':
          textColor = Colors.green;
          break;
        case 'DUE_SOON':
          textColor = Colors.orange;
          break;
        case 'OVERDUE':
          textColor = Colors.red;
          break;
        case 'RESOLVED':
          textColor = Colors.blue;
          break;
        default:
          textColor = Colors.black;
      }
    } else if (escalated == true) {
      textColor = Colors.red;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: Text(
              displayValue,
              style: TextStyle(color: textColor),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSLASection() {
    if (_complaint == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'SLA Information',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Divider(),
        _buildDetailRow('SLA Hours', _complaint!.slaHours != null ? '${_complaint!.slaHours}' : null),
        _buildDetailRow(
            'SLA Deadline',
            _complaint!.slaDeadline != null
                ? DateFormat.yMMMd().add_jm()
                    .format(DateTime.parse(_complaint!.slaDeadline!))
                : null),
        _buildDetailRow(
            'SLA Status',
            _complaint!.slaStatus ?? 'NOT_SET',
            status: _complaint!.slaStatus),
        if (_complaint!.escalationLevel != null && _complaint!.escalationLevel! > 0)
          _buildDetailRow('Escalation Level', '${_complaint!.escalationLevel}'),
        if (_complaint!.escalated == true)
          _buildDetailRow('Escalated', 'Yes',
              escalated: true),
        if (_complaint!.escalatedAt != null)
          _buildDetailRow(
              'Escalated At',
              DateFormat.yMMMd().add_jm()
                  .format(_complaint!.escalatedAt!)),
        if (_complaint!.escalationReason != null &&
            _complaint!.escalationReason!.isNotEmpty)
          _buildDetailRow('Escalation Reason', _complaint!.escalationReason),
        if (_complaint!.previousAssignedOfficer != null &&
            _complaint!.previousAssignedOfficer!.isNotEmpty)
          _buildDetailRow('Previous Assigned Officer', _complaint!.previousAssignedOfficer),
      ],
    );
  }

  Widget _buildAIAnalysisSection() {
    if (_complaint == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'AI Analysis Results',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Divider(),
        _buildDetailRow('Category', _complaint!.category),
        _buildDetailRow('Severity', _complaint!.severity),
        _buildDetailRow('Urgency Score',
            _complaint!.urgencyScore != null ? '${_complaint!.urgencyScore}' : null),
        _buildDetailRow('AI Source', _complaint!.aiSource),
        if (_complaint!.suggestedDepartment != null &&
            _complaint!.suggestedDepartment!.isNotEmpty)
          _buildDetailRow(
              'Suggested Department', _complaint!.suggestedDepartment!),
        if (_complaint!.estimatedResolutionDays != null)
          _buildDetailRow(
              'Estimated Resolution (days)',
              '${_complaint!.estimatedResolutionDays}'),
      ],
    );
  }
}