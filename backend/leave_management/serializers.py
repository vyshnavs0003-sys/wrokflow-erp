from rest_framework import serializers
from .models import LeaveType, LeavePolicy, LeaveAllocation, Holiday, LeaveRequest, LeaveAttachment

class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "description",
            "is_paid",
            "annual_quota",
            "requires_approval",
            "requires_document",
            "max_consecutive_days",
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
        annual_quota = attrs.get(
            "annual_quota",
            self.instance.annual_quota if self.instance else 0
        )

        max_consecutive_days = attrs.get(
            "max_consecutive_days",
            self.instance.max_consecutive_days if self.instance else None
        )

        if (
            max_consecutive_days
            and max_consecutive_days > annual_quota
        ):
            raise serializers.ValidationError({
                "max_consecutive_days": (
                    "Maximum consecutive days cannot be greater "
                    "than the annual quota."
                )
            })

        return attrs

class LeavePolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = LeavePolicy
        fields = [
            "id",
            "leave_type",
            "carry_forward_allowed",
            "max_carry_forward_days",
            "carry_forward_expiry_months",
            "encashment_allowed",
            "max_encashment_days",
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
        carry_forward_allowed = attrs.get(
            "carry_forward_allowed",
            self.instance.carry_forward_allowed
            if self.instance else False
        )

        max_carry_forward_days = attrs.get(
            "max_carry_forward_days",
            self.instance.max_carry_forward_days
            if self.instance else 0
        )

        carry_forward_expiry_months = attrs.get(
            "carry_forward_expiry_months",
            self.instance.carry_forward_expiry_months
            if self.instance else None
        )

        encashment_allowed = attrs.get(
            "encashment_allowed",
            self.instance.encashment_allowed
            if self.instance else False
        )

        max_encashment_days = attrs.get(
            "max_encashment_days",
            self.instance.max_encashment_days
            if self.instance else 0
        )

        if (
            not carry_forward_allowed
            and max_carry_forward_days > 0
        ):
            raise serializers.ValidationError({
                "max_carry_forward_days": (
                    "Maximum carry-forward days must be 0 "
                    "when carry-forward is not allowed."
                )
            })

        if (
            carry_forward_allowed
            and max_carry_forward_days == 0
        ):
            raise serializers.ValidationError({
                "max_carry_forward_days": (
                    "Maximum carry-forward days must be greater "
                    "than 0 when carry-forward is allowed."
                )
            })

        if (
            carry_forward_allowed
            and carry_forward_expiry_months is not None
            and carry_forward_expiry_months <= 0
        ):
            raise serializers.ValidationError({
                "carry_forward_expiry_months": (
                    "Carry-forward expiry months must be "
                    "greater than 0."
                )
            })

        if (
            not encashment_allowed
            and max_encashment_days > 0
        ):
            raise serializers.ValidationError({
                "max_encashment_days": (
                    "Maximum encashment days must be 0 "
                    "when encashment is not allowed."
                )
            })

        if (
            encashment_allowed
            and max_encashment_days == 0
        ):
            raise serializers.ValidationError({
                "max_encashment_days": (
                    "Maximum encashment days must be greater "
                    "than 0 when encashment is allowed."
                )
            })

        return attrs

class LeaveAllocationSerializer(serializers.ModelSerializer):

    used_days = serializers.ReadOnlyField()
    pending_days = serializers.ReadOnlyField()
    remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = LeaveAllocation
        fields = [
            "id",
            "employee",
            "leave_type",
            "year",
            "allocated_days",
            "carry_forward_days",
            "adjustment_days",
            "expiry_date",
            "is_active",
            "used_days",
            "pending_days",
            "remaining_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "used_days",
            "pending_days",
            "remaining_days",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        employee = attrs.get(
            "employee",
            self.instance.employee
            if self.instance else None
        )

        leave_type = attrs.get(
            "leave_type",
            self.instance.leave_type
            if self.instance else None
        )

        year = attrs.get(
            "year",
            self.instance.year
            if self.instance else None
        )

        if employee and not employee.is_active:
            raise serializers.ValidationError({
                "employee": (
                    "Leave allocation cannot be created "
                    "for an inactive employee."
                )
            })

        if employee and employee.status == "Resigned":
            raise serializers.ValidationError({
                "employee": (
                    "Leave allocation cannot be created "
                    "for a resigned employee."
                )
            })

        if leave_type and not leave_type.is_active:
            raise serializers.ValidationError({
                "leave_type": (
                    "The selected leave type is inactive."
                )
            })

        if year and year < 2000:
            raise serializers.ValidationError({
                "year": (
                    "Please provide a valid allocation year."
                )
            })

        if self.instance:
            existing_allocation = LeaveAllocation.objects.filter(
                employee=employee,
                leave_type=leave_type,
                year=year
            ).exclude(
                pk=self.instance.pk
            ).exists()
        else:
            existing_allocation = LeaveAllocation.objects.filter(
                employee=employee,
                leave_type=leave_type,
                year=year
            ).exists()

        if existing_allocation:
            raise serializers.ValidationError({
                "leave_type": (
                    "An allocation already exists for this "
                    "employee and leave type for the selected year."
                )
            })

        return attrs

class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "description",
            "is_optional",
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
        date = attrs.get(
            "date",
            self.instance.date
            if self.instance else None
        )

        if self.instance:
            existing_holiday = Holiday.objects.filter(
                date=date
            ).exclude(
                pk=self.instance.pk
            ).exists()
        else:
            existing_holiday = Holiday.objects.filter(
                date=date
            ).exists()

        if existing_holiday:
            raise serializers.ValidationError({
                "date": (
                    "A holiday already exists for the selected date."
                )
            })

        return attrs

class LeaveRequestSerializer(serializers.ModelSerializer):

    total_days = serializers.ReadOnlyField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_at",
            "reviewed_comments",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_days",
            "status",
            "reviewed_by",
            "reviewed_at",
            "reviewed_comments",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get(
            "request"
        )

        employee = attrs.get(
            "employee",
            self.instance.employee
            if self.instance else None
        )

        leave_type = attrs.get(
            "leave_type",
            self.instance.leave_type
            if self.instance else None
        )

        start_date = attrs.get(
            "start_date",
            self.instance.start_date
            if self.instance else None
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date
            if self.instance else None
        )

        if request and not request.user.is_superuser:
            if hasattr(request.user, "employee_profile"):
                employee = request.user.employee_profile

        if employee and not employee.is_active:
            raise serializers.ValidationError({
                "employee": (
                    "An inactive employee cannot request leave."
                )
            })

        if employee and employee.status == "Resigned":
            raise serializers.ValidationError({
                "employee": (
                    "A resigned employee cannot request leave."
                )
            })

        if leave_type and not leave_type.is_active:
            raise serializers.ValidationError({
                "leave_type": (
                    "The selected leave type is inactive."
                )
            })

        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    "end_date": (
                        "End date must be greater than or "
                        "equal to start date."
                    )
                })

        if employee and leave_type and start_date and end_date:
            overlapping_requests = LeaveRequest.objects.filter(
                employee=employee,
                status__in=["Pending", "Approved"],
                start_date__lte=end_date,
                end_date__gte=start_date
            )

            if self.instance:
                overlapping_requests = overlapping_requests.exclude(
                    pk=self.instance.pk
                )

            if overlapping_requests.exists():
                raise serializers.ValidationError({
                    "start_date": (
                        "This leave period overlaps with an "
                        "existing pending or approved leave request."
                    )
                })

        return attrs

    def create(self, validated_data):
        request = self.context.get(
            "request"
        )

        if request and hasattr(
            request.user,
            "employee_profile"
        ):
            validated_data["employee"] = (
                request.user.employee_profile
            )

        return LeaveRequest.objects.create(
            **validated_data
        )

class LeaveAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveAttachment
        fields = [
            "id",
            "leave_request",
            "file",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "uploaded_by",
            "uploaded_at",
        ]