'''
Docstring for portal.views
'''

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsHRUser
from portal.models import Department, Position, Employee, Attendance
from portal.serializers import *


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for Position"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee"""
    queryset = Employee.objects.all().select_related('department', 'position',
                                                     'user')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

    def get_permissions(self):
        """Admin only for create/update/delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsHRUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """Delete employee and associated user"""
        instance = self.get_object()
        employee_name = f"{instance.first_name} {instance.last_name}"

        user = instance.user

        self.perform_destroy(instance)

        if user:
            user.delete()

        return Response(
            {
                'success':
                    True,
                'message':
                    f'Employee "{employee_name}" and associated user deleted successfully'
            },
            status=status.HTTP_200_OK)


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for Attendance"""
    queryset = Attendance.objects.all().select_related('employee',
                                                       'employee__department',
                                                       'employee__position')
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        """HR/Admin can create/update, employees can view"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsHRUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Get attendance records for a specific date"""
        date_str = request.query_params.get('date')

        try:

            date = AttendanceSerializer.parse_date(date_str)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            },
                            status=status.HTTP_400_BAD_REQUEST)

        attendance = Attendance.objects.filter(
            date=date).select_related('employee')
        serializer = AttendanceSerializer(attendance, many=True)

        return Response(
            {
                'success': True,
                'date': str(date),
                'count': attendance.count(),
                'attendance': serializer.data
            },
            status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get attendance for specific employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id required'},
                            status=status.HTTP_400_BAD_REQUEST)

        attendance = Attendance.objects.filter(
            employee_id=employee_id).order_by('-date')
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get attendance for specific user"""
        user_id = request.user.id
        if not user_id:
            return Response({'error': 'user_id required'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        if user.role == 'EMPLOYEE':
            employee_id = user.employee.id
            attendance = Attendance.objects.filter(
                employee_id=employee_id).order_by('-date')
            serializer = AttendanceSerializer(attendance, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'user is not employee'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_create_or_update(self, request):
        """One-liner update_or_create"""
        # print(request.data)
        try:
            from django.db import transaction
            with transaction.atomic():
                records = request.data

                objs = [
                    Attendance(employee_id=r['employee_id'],
                               date=r['date'],
                               status=r['status']) for r in records
                ]

                Attendance.objects.bulk_create(
                    objs,
                    update_conflicts=True,
                    update_fields=['status'],
                    unique_fields=['employee', 'date'])

                return Response({
                    'success': True,
                    'processed': len(records)
                },
                                status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
