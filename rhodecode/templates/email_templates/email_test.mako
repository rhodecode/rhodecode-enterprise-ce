## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
RhodeCode test email: ${h.format_date(date)}
</%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
Test Email from RhodeCode version: ${rhodecode_version}, sent by: ${user}
</%def>

${body_plaintext()}