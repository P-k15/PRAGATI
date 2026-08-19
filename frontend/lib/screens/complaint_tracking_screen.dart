import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/complaint_model.dart';
import 'package:intl/intl.dart';

class ComplaintTrackingScreen extends StatefulWidget {
  final String complaintId;
  final String? baseUrl;

  const ComplaintTrackingScreen({Key? key, required this.complaintId, this.baseUrl}) : super(key: key);

  @override
  State<ComplaintTrackingScreen> createState() => _ComplaintTrackingScreenState();
}

class _ComplaintTrackingScreenState extends State<ComplaintTrackingScreen> {
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

  // Helper method to get SLA status color
  Color _getSlaStatusColor(String? status) {
    switch (status) {
      case 'ON_TRACK':
        return Colors.green;
      case 'DUE_SOON':
        return Colors.orange;
      case 'OVERDUE':
        return Colors.red;
      case 'RESOLVED':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Complaint Tracking'),
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
                  ? const Center(child: Text('No complaint found'))
                  : Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ListView(
                        children: [
                          Text(
                            _complaint!.description,
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          Text('Location: ${_complaint!.location}'),
                          const SizedBox(height: 16),
                          Text('Submitted: ${DateFormat.yMMMd().format(_complaint!.createdAt)}'),
                          Text('Updated: ${DateFormat.yMMMd().format(_complaint!.updatedAt)}'),
                          const SizedBox(height: 16),
                          const Divider(),
                          const Text('SLA Information:', style: TextStyle(fontWeight: FontWeight.bold)),
                          Row(
                            children: [
                              Expanded(
                                child: Text('SLA: ${_complaint!.slaHours ?? 0} hours'),
                              ),
                              if (_complaint!.slaDeadline != null)
                                Expanded(
                                  child: Text(
                                    'Deadline: ${DateFormat.yMMMd().add_jm().format(DateTime.parse(_complaint!.slaDeadline!))}',
                                    textAlign: TextAlign.end,
                                  ),
                                ),
                            ],
                          ),
                          // SLA Status with color
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Row(
                              children: [
                                const Text('Status: '),
                                Text(
                                  _complaint!.slaStatus ?? 'NOT_SET',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: _getSlaStatusColor(_complaint!.slaStatus),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Escalation information
                          if (_complaint!.escalationLevel != null && _complaint!.escalationLevel! > 0)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2.0),
                              child: Text('Escalation Level: ${_complaint!.escalationLevel}',
                                  style: TextStyle(color: Colors.red)),
                            ),
                          if (_complaint!.escalated == true)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2.0),
                              child: const Text('Escalated: Yes',
                                  style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                            ),
                          if (_complaint!.escalatedAt != null)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2.0),
                              child: Text('Escalated At: ${DateFormat.yMMMd().add_jm().format(_complaint!.escalatedAt!)}'),
                            ),
                          if (_complaint!.escalationReason != null &&
                              _complaint!.escalationReason!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2.0),
                              child: Text('Escalation Reason: ${_complaint!.escalationReason}'),
                            ),
                          if (_complaint!.previousAssignedOfficer != null &&
                              _complaint!.previousAssignedOfficer!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2.0),
                              child: Text('Previous Officer: ${_complaint!.previousAssignedOfficer}'),
                            ),
                          const SizedBox(height: 16),
                          const Divider(),
                          const Text('AI Analysis:', style: TextStyle(fontWeight: FontWeight.bold)),
                          Text('Category: ${_complaint!.category ?? 'N/A'}'),
                          Text('Subcategory: ${_complaint!.subcategory ?? 'N/A'}'),
                          Text('Severity: ${_complaint!.severity ?? 'N/A'}'),
                          Text('Priority: ${_complaint!.priority ?? 'N/A'}'),
                          Text('Department: ${_complaint!.department ?? 'N/A'}'),
                          Text('Summary: ${_complaint!.summary ?? 'N/A'}'),
                          const SizedBox(height: 16),
                          const Divider(),
                          const Text('Status Information:', style: TextStyle(fontWeight: FontWeight.bold)),
                          Text('Status: ${_complaint!.status ?? 'N/A'}'),
                          if (_complaint!.assignedOfficer != null)
                            Text('Assigned Officer: ${_complaint!.assignedOfficer}'),
                          if (_complaint!.resolvedAt != null)
                            Text('Resolved: ${DateFormat.yMMMd().format(_complaint!.resolvedAt!)}'),
                        ],
                      ),
                    ),
          );
  }
}