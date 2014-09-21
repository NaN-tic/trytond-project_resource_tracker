=================================
Project Resource Tracker Scenario
=================================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()
    >>> now = datetime.datetime.now()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install project_invoice::

    >>> Module = Model.get('ir.module.module')
    >>> module, = Module.find([
    ...         ('name', '=', 'project_resource_tracker'),
    ...     ])
    >>> Module.install([module.id], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='Euro', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
    ...         mon_decimal_point='.')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find()

Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> config._context = User.get_preferences(True, config.context)

Create party::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create trackers::

    >>> Tracker = Model.get('project.work.tracker')
    >>> development = Tracker(name='Development')
    >>> development.save()
    >>> issue = Tracker(name='Issue')
    >>> issue.save()

Create employees::

    >>> Employee = Model.get('company.employee')
    >>> employee = Employee()
    >>> party = Party(name='Employee')
    >>> party.save()
    >>> employee.party = party
    >>> employee.company = company
    >>> employee.trackers.append(development)
    >>> employee.save()

    >>> second_employee = Employee()
    >>> party = Party(name='Second Employee')
    >>> party.save()
    >>> second_employee.party = party
    >>> second_employee.company = company
    >>> second_employee.trackers.append(issue)
    >>> second_employee.save()

Configure Resources::

    >>> Config = Model.get('resource.configuration')
    >>> IRModel = Model.get('ir.model')
    >>> model, = IRModel.find([('model', '=', 'project.work')])
    >>> config = Config(1)
    >>> config.documents.append(model)
    >>> config.save()

Create resources for employees::

    >>> Calendar = Model.get('calendar.calendar')
    >>> Resource = Model.get('resource.resource')
    >>> calendar = Calendar()
    >>> calendar.name = 'Employee'
    >>> calendar.save()
    >>> resource = Resource()
    >>> resource.name = 'Employee'
    >>> resource.calendar = calendar
    >>> resource.employee = employee
    >>> resource.save()

    >>> calendar = Calendar()
    >>> calendar.name = 'Second Employee'
    >>> calendar.save()
    >>> resource = Resource()
    >>> resource.name = 'Second Employee'
    >>> resource.calendar = calendar
    >>> resource.employee = second_employee
    >>> resource.save()

Create a Project::

    >>> ProjectWork = Model.get('project.work')
    >>> TimesheetWork = Model.get('timesheet.work')
    >>> project = ProjectWork()
    >>> work = TimesheetWork()
    >>> work.name = 'Test Resource Plan'
    >>> work.save()
    >>> project.work = work
    >>> project.type = 'project'
    >>> work = TimesheetWork()
    >>> work.name = 'Task 1'
    >>> work.save()
    >>> task = project.children.new()
    >>> task.work = work
    >>> task.type = 'task'
    >>> task.effort = 16
    >>> task.tracker = development
    >>> work = TimesheetWork()
    >>> work.name = 'Task 2'
    >>> work.save()
    >>> task = project.children.new()
    >>> task.work = work
    >>> task.type = 'task'
    >>> task.effort = 4
    >>> task.tracker = issue
    >>> project.save()
    >>> task_1, task_2= project.children

Plan all tasks and check that are correcly assigned::

    >>> plan = Wizard('project.resource.plan')
    >>> plan.form.domain = ''
    >>> plan.form.order = ''
    >>> plan.form.confirm_bookings = True
    >>> plan.execute('tasks')
    >>> plan.execute('plan')
    >>> task_1.reload()
    >>> task_1.assigned_employee == employee
    True
    >>> task_2.reload()
    >>> task_2.assigned_employee == second_employee
    True
