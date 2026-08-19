import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/complaint_model.dart';
import 'package:intl/intl.dart';

class OfficerDashboardScreen extends StatefulWidget {
  final String? baseUrl;
  final String? officerId; // Officer ID to filter complaints for

  const OfficerDashboardScreen({
    Key? key,
    this.baseUrl,
    this.officerId,
  }) : super(key: key);

  @override
  State<OfficerDashboardScreen> createState() => _OfficerDashboardScreenState();
}

class _OfficerDashboardScreenState extends State<OfficerDashboardScreen> {
  late final ApiService _apiService;
  List<ComplaintModel> _officerComplaints = [];
  bool _isLoading = false;
  String? _errorMessage;
  String? _officerName;
  String? _officerDepartment;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(baseUrl: widget.baseUrl);
    _loadOfficerData();
    _loadComplaints();
  }

  Future<void> _loadOfficerData() async {
    // For demo purposes, we'll map the known officer email to officer data
    // In a real app, this would come from an API call or user session
    if (widget.officerId != null) {
      // Mock officer data based on seed_officers.py
      // In a real implementation, this would fetch from backend
      switch (widget.officerId) {
        case 'officer_001':
          _officerName = 'Officer A';
          _officerDepartment = 'Electrical Maintenance';
          break;
        case 'officer_002':
          _officerName = 'Officer B';
          _officerDepartment = 'Electrical Maintenance';
          break;
        case 'officer_003':
          _officerName = 'Officer C';
          _officerDepartment = 'Sanitation';
          break;
        case 'officer_004':
          _officerName = 'Officer D';
          _officerDepartment = 'Sanitation';
          break;
        case 'officer_005':
          _officerName = 'Officer E';
          _officerDepartment = 'Water Works';
          break;
        case 'officer_006':
          _officerName = 'Officer F';
          _officerDepartment = 'Water Works';
          break;
        case 'officer_007':
          _officerName = 'Officer G';
          _officerDepartment = 'Road Maintenance';
          break;
        case 'officer_008':
          _officerName = 'Officer H';
          _officerDepartment = 'Road Maintenance';
          break;
        default:
          _officerName = 'Officer';
          _officerDepartment = 'Unknown';
      }
    } else {
      // Fallback if no officer ID provided
      _officerName = 'Officer';
      _officerDepartment = 'Unknown';
    }
  }

  Future<void> _loadComplaints() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final complaints = await _apiService.getComplaints();
      // Filter complaints assigned to this officer
      if (widget.officerId != null && widget.officerId!.isNotEmpty) {
        _officerComplaints = complaints.where((complaint) {
          return complaint.assignedOfficer == widget.officerId;
        }).toList();
      } else {
        // If no officer ID specified, show all complaints (fallback)
        _officerComplaints = complaints;
      }
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

  Future<void> _refreshComplaints() async {
    await _loadComplaints();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Officer Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: _refreshComplaints,
          ),
        ],
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
                        onPressed: _refreshComplaints,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _officerComplaints.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.inbox,
                            size: 48,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            widget.officerId != null
                                ? 'No complaints assigned to you'
                                : 'No complaints found',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Colors.grey,
                            ),
                          ),
                          const SizedBox(height: 24),
                          ElevatedButton(
                            onPressed: _refreshComplaints,
                            child: const Text('Refresh'),
                          ),
                        ],
                      ),
                    )
                  : Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ListView(
                        children: [
                          // Officer Info Header
                          _buildOfficerHeader(),
                          const SizedBox(height: 24),

                          // Summary Statistics
                          _buildSummaryStatistics(),
                          const SizedBox(height: 24),

                          // Complaints List Header
                          const Padding(
                            padding: EdgeInsets.only(bottom: 8.0),
                            child: Text(
                              'My Assigned Complaints',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),

                          // Complaints List
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: _officerComplaints.length,
                            itemBuilder: (context, index) {
                              return _buildComplaintCard(
                                _officerComplaints[index],
                              );
                            },
                          ),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildOfficerHeader() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Officer Dashboard',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Welcome, $_officerName',
              style: const TextStyle(
                fontSize: 16,
                color: Colors.black87,
              ),
            ),
            Text(
              'Department: $_officerDepartment',
              style: const TextStyle(
                fontSize: 16,
                color: Colors.black87,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryStatistics() {
    // Calculate statistics
    int assignedCount = _officerComplaints.length;
    int inProgressCount = _officerComplaints.where((c) => c.status == 'IN_PROGRESS').length;
    int dueSoonCount = _officerComplaints.where((c) => c.slaStatus == 'DUE_SOON').length;
    int overdueCount = _officerComplaints.where((c) => c.slaStatus == 'OVERDUE').length;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              'Complaint Summary',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatBox('Assigned', assignedCount.toString(), Colors.blue),
                _buildStatBox('In Progress', inProgressCount.toString(), Colors.orange),
                _buildStatBox('Due Soon', dueSoonCount.toString(), Colors.amber),
                _buildStatBox('Overdue', overdueCount.toString(), Colors.red),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildComplaintCard(ComplaintModel complaint) {
    // Determine status colors
    Color getStatusColor(String? status) {
      switch (status) {
        case 'SUBMITTED':
          return Colors.grey;
        case 'AI_PROCESSED':
          return Colors.blue;
        case 'ASSIGNED':
          return Colors.indigo;
        case 'IN_PROGRESS':
          return Colors.orange;
        case 'RESOLVED':
          return Colors.green;
        default:
          return Colors.grey;
      }
    }

    // Determine SLA status colors
    Color getSlaColor(String? slaStatus) {
      switch (slaStatus) {
        case 'ON_TRACK':
          return Colors.green;
        case 'DUE_SOON':
          return Colors.amber;
        case 'OVERDUE':
          return Colors.red;
        case 'RESOLVED':
          return Colors.green;
        default:
          return Colors.grey;
      }
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () {
          Navigator.of(context).pushNamed(
            '/complaint-details',
            arguments: complaint.id,
          );
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Complaint ID and Status Badges
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'ID: ${complaint.id}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: getStatusColor(complaint.status).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      complaint.status ?? 'N/A',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: getStatusColor(complaint.status),
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: getSlaColor(complaint.slaStatus).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      complaint.slaStatus ?? 'NOT_SET',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: getSlaColor(complaint.slaStatus),
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Description
              Text(
                complaint.description,
                style: const TextStyle(
                  fontSize: 14,
                  height: 1.4,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),

              // Details Row
              Row(
                children: [
                  Expanded(
                    child: _buildDetailChip(
                      'Category',
                      complaint.category ?? 'N/A',
                    ),
                  ),
                  Expanded(
                    child: _buildDetailChip(
                      'Priority',
                      complaint.priority ?? 'N/A',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildDetailChip(
                      'Created',
                      DateFormat.yMMMd().format(complaint.createdAt),
                    ),
                  ),
                  Expanded(
                    child: _buildDetailChip(
                      'SLA',
                      '${complaint.slaHours ?? 0} hrs',
                    ),
                  ),
                ],
              ),
              if (complaint.escalated == true) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        color: Colors.red,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'ESCALATED (Level ${complaint.escalationLevel})',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.red,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        border: Border.all(
          color: Colors.grey[300]!,
        ),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}