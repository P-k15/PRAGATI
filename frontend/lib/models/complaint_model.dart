class ComplaintModel {
  final String id;
  final String citizenId;
  final String description;
  final String location;
  final String? category;
  final String? subcategory;
  final String? severity;
  final String? priority;
  final String? department;
  final int? slaHours;
  final String? slaDeadline;
  // SLA Monitoring & Escalation (Phase 5.3)
  final String? slaStatus; // ON_TRACK, DUE_SOON, OVERDUE, RESOLVED
  final int? escalationLevel;
  final bool? escalated;
  final DateTime? escalatedAt;
  final String? escalationReason;
  final String? previousAssignedOfficer;
  final String? summary;
  final String? status;
  final String? aiSource;
  final double? latitude;
  final double? longitude;
  final String? assignedOfficer;
  final DateTime? assignedAt;
  final DateTime? resolvedAt;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int? urgencyScore;
  final String? suggestedDepartment;
  final int? estimatedResolutionDays;
  // AI Decision Engine fields (Phase 5.1)
  final String? recommendedAction;
  final double? confidence;
  // Routing fields (Phase 5.2)
  final String? routingSource;
  final String? routingReason;

  ComplaintModel({
    required this.id,
    required this.citizenId,
    required this.description,
    required this.location,
    this.category,
    this.subcategory,
    this.severity,
    this.priority,
    this.department,
    this.slaHours,
    this.slaDeadline,
    this.slaStatus,
    this.escalationLevel,
    this.escalated,
    this.escalatedAt,
    this.escalationReason,
    this.previousAssignedOfficer,
    this.summary,
    this.status,
    this.aiSource,
    this.latitude,
    this.longitude,
    this.assignedOfficer,
    this.assignedAt,
    this.resolvedAt,
    required this.createdAt,
    required this.updatedAt,
    this.urgencyScore,
    this.suggestedDepartment,
    this.estimatedResolutionDays,
    // AI Decision Engine fields (Phase 5.1)
    this.recommendedAction,
    this.confidence,
    // Routing fields (Phase 5.2)
    this.routingSource,
    this.routingReason,
  });

  factory ComplaintModel.fromJson(Map<String, dynamic> json) {
    return ComplaintModel(
      id: json['id']?.toString() ?? '',
      citizenId: json['citizen_id']?.toString() ?? 'anonymous_citizen',
      description: json['description']?.toString() ?? '',
      location: json['location']?.toString() ?? '',
      category: json['category']?.toString(),
      subcategory: json['subcategory']?.toString(),
      severity: json['severity']?.toString(),
      priority: json['priority']?.toString(),
      department: json['department']?.toString(),
      slaHours: json['sla_hours'] is int ? json['sla_hours'] as int : (json['sla_hours'] is num ? (json['sla_hours'] as num).toInt() : null),
      slaDeadline: json['sla_deadline']?.toString(),
      // SLA Monitoring & Escalation (Phase 5.3)
      slaStatus: json['sla_status']?.toString(),
      escalationLevel: json['escalation_level'] is int ? json['escalation_level'] as int : (json['escalation_level'] is num ? (json['escalation_level'] as num).toInt() : null),
      escalated: json['escalated'] is bool ? json['escalated'] as bool : (json['escalated'] is int ? json['escalated'] == 1 : null),
      escalatedAt: json['escalated_at'] != null ? DateTime.tryParse(json['escalated_at'].toString()) : null,
      escalationReason: json['escalation_reason']?.toString(),
      previousAssignedOfficer: json['previous_assigned_officer']?.toString(),
      summary: json['summary']?.toString(),
      status: json['status']?.toString(),
      aiSource: json['ai_source']?.toString(),
      latitude: json['latitude'] is double ? json['latitude'] as double : (json['latitude'] is num ? (json['latitude'] as num).toDouble() : null),
      longitude: json['longitude'] is double ? json['longitude'] as double : (json['longitude'] is num ? (json['longitude'] as num).toDouble() : null),
      assignedOfficer: json['assigned_officer']?.toString(),
      assignedAt: json['assigned_at'] != null ? DateTime.tryParse(json['assigned_at'].toString()) : null,
      resolvedAt: json['resolved_at'] != null ? DateTime.tryParse(json['resolved_at'].toString()) : null,
      createdAt: json['created_at'] != null ? (DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()) : DateTime.now(),
      updatedAt: json['updated_at'] != null ? (DateTime.tryParse(json['updated_at'].toString()) ?? DateTime.now()) : DateTime.now(),
      urgencyScore: json['urgency_score'] is int ? json['urgency_score'] as int : (json['urgency_score'] is num ? (json['urgency_score'] as num).toInt() : null),
      suggestedDepartment: json['suggested_department']?.toString(),
      estimatedResolutionDays: json['estimated_resolution_days'] is int ? json['estimated_resolution_days'] as int : (json['estimated_resolution_days'] is num ? (json['estimated_resolution_days'] as num).toInt() : null),
      // AI Decision Engine fields
      recommendedAction: json['recommended_action']?.toString(),
      confidence: (json['confidence'] is num) ? (json['confidence'] as num).toDouble() : null,
      // Routing fields
      routingSource: json['routing_source']?.toString(),
      routingReason: json['routing_reason']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'citizen_id': citizenId,
      'description': description,
      'location': location,
      'category': category,
      'subcategory': subcategory,
      'severity': severity,
      'priority': priority,
      'department': department,
      'sla_hours': slaHours,
      'sla_deadline': slaDeadline,
      // SLA Monitoring & Escalation (Phase 5.3)
      'sla_status': slaStatus,
      'escalation_level': escalationLevel,
      'escalated': escalated,
      'escalated_at': escalatedAt?.toIso8601String(),
      'escalation_reason': escalationReason,
      'previous_assigned_officer': previousAssignedOfficer,
      'summary': summary,
      'status': status,
      'ai_source': aiSource,
      'latitude': latitude,
      'longitude': longitude,
      'assigned_officer': assignedOfficer,
      'assigned_at': assignedAt?.toIso8601String(),
      'resolved_at': resolvedAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'urgency_score': urgencyScore,
      'suggested_department': suggestedDepartment,
      'estimated_resolution_days': estimatedResolutionDays,
      // AI Decision Engine fields (Phase 5.1)
      'recommended_action': recommendedAction,
      'confidence': confidence,
      // Routing fields (Phase 5.2)
      'routing_source': routingSource,
      'routing_reason': routingReason,
    };
  }
}