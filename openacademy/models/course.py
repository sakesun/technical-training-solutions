# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'Course'

    name = fields.Char(name='Title', required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('openacademy.partner', string="Responsible")
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")
    level = fields.Selection([('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], string="Difficulty Level")
    session_count = fields.Integer("Session Count", compute="_compute_session_count")

    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)


class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'Session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=lambda self: fields.Date.today())
    end_date = fields.Date(default=fields.Date.today)
    active = fields.Boolean(default=True)
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1)
    instructor_id = fields.Many2one('openacademy.partner', string="Instructor")
    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('openacademy.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken seats", compute='_compute_taken_seats')
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('done', "Done")], default='draft')
    level = fields.Selection(related='course_id.level', readonly=True)
    responsible_id = fields.Many2one(related='course_id.responsible_id', readonly=True, store=True)
    description = fields.Html()

    seats = fields.Integer(string='Seats')
    attendees_count = fields.Integer(string="Attendees count", compute='_get_attendees_count', store=True)

    @api.depends('seats', 'attendee_ids')
    def _compute_taken_seats(self):
        for session in self:
            if not session.seats:
                session.taken_seats = 0.0
            else:
                session.taken_seats = 100.0 * len(session.attendee_ids) / session.seats

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for session in self:
            session.attendees_count = len(session.attendee_ids)

    @api.onchange('start_date', 'end_date')
    def _compute_duration(self):
        if not (self.start_date and self.end_date):
            return
        if self.end_date < self.start_date:
            return {'warning': {
                'title': "Incorrect date value",
                'message': "End date is earlier then start date",
            }}
        delta = fields.Date.from_string(self.end_date) - fields.Date.from_string(self.start_date)
        self.duration = delta.days + 1
