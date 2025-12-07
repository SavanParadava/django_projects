from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from portal.models import Department, Position, Employee, Attendance
from accounts.serializers import RegisterSerializer
from portal.models import Employee

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""

    class Meta:
        model = Department
        fields = ['id', 'name']
        read_only_fields = ['id']


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for Position model"""

    class Meta:
        model = Position
        fields = ['id', 'title']
        read_only_fields = ['id']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Simplified employee serializer for lists"""
    department_name = serializers.CharField(source='department.name',
                                            read_only=True)
    position_title = serializers.CharField(source='position.title',
                                           read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'hire_date',
            'department_name',
            'position_title',
        ]
        read_only_fields = [
            'id', 'hire_date', 'department_name', 'position_title', 'username'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed employee serializer with related objects"""
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=False)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        source='position',
        write_only=True,
        required=False)
    user = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'user',
            'hire_date',
            'department',
            'department_id',
            'position',
            'position_id',
        ]
        read_only_fields = ['id', 'hire_date', 'user']

    def get_user(self, obj):
        """Return user info if employee has associated user"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'role': obj.user.role,
            }
        return None

    def get_full_name(self, obj):
        """Return full name"""
        return f"{obj.first_name} {obj.last_name}"


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating employees"""
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', required=False)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), source='position', required=False)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])

    class Meta:
        model = Employee
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'department_id',
            'position_id',
        ]

    def create(self, validated_data):
        """Create user first, then employee"""
        print(validated_data)
        user_data = {key: validated_data[key] for key in validated_data.keys()}
        validated_data.pop('username')
        validated_data.pop('password')
        user_data['password2'] = user_data['password']

        user_serializer = RegisterSerializer(data=user_data)
        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        user = user_serializer.save()

        employee = Employee.objects.create(user=user, **validated_data)
        return employee

    def update(self, instance, validated_data):
        """Update employee and associated user"""

        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        instance.department_id = validated_data.get('department_id',
                                                    instance.department_id)

        instance.position_id = validated_data.get('position_id',
                                                  instance.position_id)

        instance.save()

        if instance.user:
            instance.user.first_name = instance.first_name
            instance.user.last_name = instance.last_name
            instance.user.email = instance.email
            instance.user.username = instance.username
            instance.user.save()

        return instance

    def validate_email(self, value):
        """Validate email is unique"""
        if Employee.objects.filter(email=value).exclude(
                pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Employee email must be unique')
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
    )
    date = serializers.DateField(
        format='%Y-%m-%d',
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'],
        required=False)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee_id',
            'employee_name',
            'date',
            'status',
        ]
        read_only_fields = ['id', 'employee_name']

    def get_employee_name(self, obj):
        """Return full name of employee"""
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    @staticmethod
    def parse_date(date_str):
        """Parse date from multiple formats"""

        if not date_str:
            return timezone.now().date()

        date_field = serializers.DateField(
            format='%Y-%m-%d',
            input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'])

        return date_field.to_internal_value(date_str)
