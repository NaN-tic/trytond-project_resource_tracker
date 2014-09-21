# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields, ModelSQL
from trytond.pool import PoolMeta

__all__ = ['EmployeeTrackers', 'Employee', 'Work']
__metaclass__ = PoolMeta


class EmployeeTrackers(ModelSQL):
    'Employee - Trackers'
    __name__ = 'project.tracker-company.employee'
    _table = 'tracker_employee_rel'

    employee = fields.Many2One('company.employee', 'Employee',
        ondelete='CASCADE', select=True)
    tracker = fields.Many2One('project.work.tracker', 'Tracker',
        ondelete='CASCADE', select=True)


class Employee:
    __name__ = 'company.employee'

    trackers = fields.Many2Many('project.tracker-company.employee', 'employee',
        'tracker', 'Trackers')


class Work:
    __name__ = 'project.work'

    def get_free_resource_domain(self):
        domain = super(Work, self).get_free_resource_domain()
        if self.tracker:
            domain.append(('employee.trackers', '=', self.tracker.id))
        return domain
