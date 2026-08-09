from rest_framework import serializers
from django.db.models import Q
from django.utils import timezone
from .models import (
    Shift,
    EmployeeShiftAssignment,
    Attendance,
    AttendanceRegularization,
    AttendanceAdjustment,
    AttendanceLog,
    AttendanceAttachment,
    Overtime,
)


class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift

        fields = [
            "id",
            "name",
            "start_time",
            "end_time",
            "grace_time_minutes",
            "minimum_half_day_hours",
            "minimum_full_day_hours",
            "is_night_shift",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        start_time = attrs.get(
            "start_time",
            self.instance.start_time
            if self.instance
            else None
        )

        end_time = attrs.get(
            "end_time",
            self.instance.end_time
            if self.instance
            else None
        )

        is_night_shift = attrs.get(
            "is_night_shift",
            self.instance.is_night_shift
            if self.instance
            else False
        )

        minimum_half_day_hours = attrs.get(
            "minimum_half_day_hours",
            self.instance.minimum_half_day_hours
            if self.instance
            else 4.00
        )

        minimum_full_day_hours = attrs.get(
            "minimum_full_day_hours",
            self.instance.minimum_full_day_hours
            if self.instance
            else 8.00
        )

        if (
            not is_night_shift
            and start_time
            and end_time
            and end_time <= start_time
        ):
            raise serializers.ValidationError({
                "end_time": (
                    "End time must be greater than start time "
                    "for a non-night shift."
                )
            })

        if minimum_half_day_hours <= 0:
            raise serializers.ValidationError({
                "minimum_half_day_hours": (
                    "Minimum half-day hours must be greater than 0."
                )
            })

        if minimum_full_day_hours <= 0:
            raise serializers.ValidationError({
                "minimum_full_day_hours": (
                    "Minimum full-day hours must be greater than 0."
                )
            })

        if minimum_half_day_hours > minimum_full_day_hours:
            raise serializers.ValidationError({
                "minimum_half_day_hours": (
                    "Minimum half-day hours cannot be greater "
                    "than minimum full-day hours."
                )
            })

        return attrs


class EmployeeShiftAssignmentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EmployeeShiftAssignment

        fields = [
            "id",
            "employee",
            "shift",
            "effective_from",
            "effective_to",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        employee = attrs.get(
            "employee",
            self.instance.employee
            if self.instance
            else None
        )

        shift = attrs.get(
            "shift",
            self.instance.shift
            if self.instance
            else None
        )

        effective_from = attrs.get(
            "effective_from",
            self.instance.effective_from
            if self.instance
            else None
        )

        effective_to = attrs.get(
            "effective_to",
            self.instance.effective_to
            if self.instance
            else None
        )

        is_active = attrs.get(
            "is_active",
            self.instance.is_active
            if self.instance
            else True
        )

        if employee and not employee.is_active:
            raise serializers.ValidationError({
                "employee": (
                    "An inactive employee cannot be assigned to a shift."
                )
            })

        if employee and employee.status == "Resigned":
            raise serializers.ValidationError({
                "employee": (
                    "A resigned employee cannot be assigned to a shift."
                )
            })

        if shift and not shift.is_active:
            raise serializers.ValidationError({
                "shift": (
                    "The selected shift is inactive."
                )
            })

        if (
            effective_from
            and effective_to
            and effective_to < effective_from
        ):
            raise serializers.ValidationError({
                "effective_to": (
                    "Effective to date cannot be before "
                    "effective from date."
                )
            })

        if employee and effective_from and is_active:

            overlapping = (
                EmployeeShiftAssignment.objects.filter(
                    employee=employee,
                    is_active=True,
                    effective_from__lte=(
                        effective_to
                        if effective_to
                        else effective_from
                    ),
                )
            )

            if self.instance:
                overlapping = overlapping.exclude(
                    pk=self.instance.pk
                )

            for assignment in overlapping:

                existing_end = assignment.effective_to

                if (
                    existing_end is None
                    or existing_end >= effective_from
                ):
                    raise serializers.ValidationError({
                        "employee": (
                            "This employee already has an "
                            "overlapping active shift assignment."
                        )
                    })

        return attrs


class AttendanceSerializer(serializers.ModelSerializer):

    worked_hours = serializers.ReadOnlyField()
    late_minutes = serializers.ReadOnlyField()
    early_exit_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Attendance

        fields = [
            "id",
            "employee",
            "shift",
            "attendance_date",
            "check_in",
            "check_out",
            "worked_hours",
            "late_minutes",
            "early_exit_minutes",
            "status",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "worked_hours",
            "late_minutes",
            "early_exit_minutes",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        employee = attrs.get(
            "employee",
            self.instance.employee
            if self.instance
            else None
        )

        shift = attrs.get(
            "shift",
            self.instance.shift
            if self.instance
            else None
        )

        attendance_date = attrs.get(
            "attendance_date",
            self.instance.attendance_date
            if self.instance
            else None
        )

        check_in = attrs.get(
            "check_in",
            self.instance.check_in
            if self.instance
            else None
        )

        check_out = attrs.get(
            "check_out",
            self.instance.check_out
            if self.instance
            else None
        )

        if employee and not employee.is_active:
            raise serializers.ValidationError({
                "employee": (
                    "Attendance cannot be recorded "
                    "for an inactive employee."
                )
            })

        if employee and employee.status == "Resigned":
            raise serializers.ValidationError({
                "employee": (
                    "Attendance cannot be recorded "
                    "for a resigned employee."
                )
            })

        if shift and not shift.is_active:
            raise serializers.ValidationError({
                "shift": (
                    "The selected shift is inactive."
                )
            })

        if check_in and check_out:
            if check_out < check_in:
                raise serializers.ValidationError({
                    "check_out": (
                        "Check-out cannot be earlier "
                        "than check-in."
                    )
                })

        if check_in and attendance_date:

            if check_in.date() != attendance_date:
                raise serializers.ValidationError({
                    "check_in": (
                        "Check-in date must match "
                        "the attendance date."
                    )
                })

        if check_out and attendance_date:

            valid_checkout_date = (
                check_out.date() == attendance_date
            )

            if shift and shift.is_night_shift:

                valid_checkout_date = (
                    check_out.date()
                    in [
                        attendance_date,
                        attendance_date
                        + timezone.timedelta(days=1),
                    ]
                )

            if not valid_checkout_date:
                raise serializers.ValidationError({
                    "check_out": (
                        "Check-out date must match the "
                        "attendance date, or the following "
                        "day for a night shift."
                    )
                })

        if employee and attendance_date:

            existing = Attendance.objects.filter(
                employee=employee,
                attendance_date=attendance_date,
            )

            if self.instance:
                existing = existing.exclude(
                    pk=self.instance.pk
                )

            if existing.exists():
                raise serializers.ValidationError({
                    "attendance_date": (
                        "Attendance already exists for "
                        "this employee on this date."
                    )
                })

        if employee and shift and attendance_date:

            assignment_exists = (
                EmployeeShiftAssignment.objects.filter(
                    employee=employee,
                    shift=shift,
                    effective_from__lte=attendance_date,
                    is_active=True,
                )
                .filter(
                    Q(
                        effective_to__isnull=True
                    )
                    | Q(
                        effective_to__gte=attendance_date
                    )
                )
                .exists()
            )

            if not assignment_exists:
                raise serializers.ValidationError({
                    "shift": (
                        "The selected shift is not assigned "
                        "to this employee for the attendance "
                        "date."
                    )
                })

        return attrs


class AttendanceRegularizationSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AttendanceRegularization

        fields = [
            "id",
            "attendance",
            "requested_check_in",
            "requested_check_out",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_at",
            "reviewed_comments",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "reviewed_by",
            "reviewed_at",
            "reviewed_comments",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        attendance = attrs.get(
            "attendance",
            self.instance.attendance
            if self.instance
            else None
        )

        requested_check_in = attrs.get(
            "requested_check_in",
            self.instance.requested_check_in
            if self.instance
            else None
        )

        requested_check_out = attrs.get(
            "requested_check_out",
            self.instance.requested_check_out
            if self.instance
            else None
        )

        reason = attrs.get(
            "reason",
            self.instance.reason
            if self.instance
            else None
        )

        if not attendance:
            raise serializers.ValidationError({
                "attendance": (
                    "Attendance record is required."
                )
            })

        if not reason:
            raise serializers.ValidationError({
                "reason": (
                    "Reason is required for regularization."
                )
            })

        if (
            requested_check_in
            and requested_check_out
            and requested_check_out < requested_check_in
        ):
            raise serializers.ValidationError({
                "requested_check_out": (
                    "Requested check-out cannot be earlier "
                    "than requested check-in."
                )
            })

        if self.instance is None:

            if hasattr(
                attendance,
                "regularization"
            ):
                raise serializers.ValidationError({
                    "attendance": (
                        "A regularization request already "
                        "exists for this attendance record."
                    )
                })

        return attrs


class AttendanceAdjustmentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AttendanceAdjustment

        fields = [
            "id",
            "attendance",
            "adjustment_type",
            "minutes",
            "reason",
            "adjusted_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "adjusted_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        attendance = attrs.get(
            "attendance"
        )

        minutes = attrs.get(
            "minutes"
        )

        reason = attrs.get(
            "reason"
        )

        if not attendance:
            raise serializers.ValidationError({
                "attendance": (
                    "Attendance record is required."
                )
            })

        if not minutes or minutes <= 0:
            raise serializers.ValidationError({
                "minutes": (
                    "Adjustment minutes must be greater than 0."
                )
            })

        if not reason:
            raise serializers.ValidationError({
                "reason": (
                    "Reason is required for an attendance adjustment."
                )
            })

        return attrs


class AttendanceLogSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AttendanceLog

        fields = [
            "id",
            "attendance",
            "action",
            "performed_by",
            "remarks",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "performed_by",
            "created_at",
        ]


class AttendanceAttachmentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AttendanceAttachment

        fields = [
            "id",
            "attendance",
            "file",
            "uploaded_by",
            "uploaded_at",
        ]

        read_only_fields = [
            "id",
            "uploaded_by",
            "uploaded_at",
        ]

    def validate(self, attrs):

        attendance = attrs.get(
            "attendance"
        )

        file = attrs.get(
            "file"
        )

        if not attendance:
            raise serializers.ValidationError({
                "attendance": (
                    "Attendance record is required."
                )
            })

        if not file:
            raise serializers.ValidationError({
                "file": (
                    "Attachment file is required."
                )
            })

        return attrs


class OvertimeSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Overtime

        fields = [
            "id",
            "attendance",
            "overtime_minutes",
            "reason",
            "status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        attendance = attrs.get(
            "attendance"
        )

        overtime_minutes = attrs.get(
            "overtime_minutes"
        )

        reason = attrs.get(
            "reason"
        )

        if not attendance:
            raise serializers.ValidationError({
                "attendance": (
                    "Attendance record is required."
                )
            })

        if not overtime_minutes or overtime_minutes <= 0:
            raise serializers.ValidationError({
                "overtime_minutes": (
                    "Overtime minutes must be greater than 0."
                )
            })

        if (
            attendance.check_in
            and attendance.check_out
        ):

            if attendance.worked_hours <= 0:
                raise serializers.ValidationError({
                    "attendance": (
                        "Overtime cannot be recorded "
                        "for an attendance record with "
                        "zero worked hours."
                    )
                })

        if not reason:
            raise serializers.ValidationError({
                "reason": (
                    "Reason is required for overtime."
                )
            })

        if self.instance is None:

            if hasattr(
                attendance,
                "overtime"
            ):
                raise serializers.ValidationError({
                    "attendance": (
                        "Overtime already exists for "
                        "this attendance record."
                    )
                })

        return attrs